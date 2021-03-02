import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from typing import Optional
from entities.posts import Post as Post2
from entities.posts import PostItem, PostItemType, PostListResult
from services import schema
from services.base import BaseService
from services.entities import Post
from services.exceptions import PostNotFound
from services.profile import ProfileService

logger = logging.getLogger(__name__)


class PostService(BaseService):
    async def list(self, offset: int = 0, limit: int = 10) -> PostListResult:
        """List posts.

        :param offset: the number of posts to skip
        :param limit: the number of posts to fetch
        :return: the list query result
        """

        posts_statement = sa.select([schema.posts.c.shortcode])\
            .select_from(schema.posts)\
            .order_by(schema.posts.c.creation_time.desc())\
            .offset(offset).limit(limit)
        statement = sa.select([
            schema.posts.c.shortcode,
            schema.posts.c.owner_username,
            schema.posts.c.creation_time,
            schema.posts.c.type,
            schema.posts.c.caption,
            schema.posts.c.caption_hashtags,
            schema.posts.c.caption_mentions,
            schema.post_items.c.type.label('item_type'),
            schema.post_items.c.duration.label('item_duration'),
            schema.post_items.c.filename.label('item_filename'),
            schema.post_items.c.thumb_image_filename.label('item_thumb_image_filename'),
        ]).select_from(
            schema.posts.join(schema.post_items, schema.posts.c.shortcode == schema.post_items.c.post_shortcode)
        ).where(
            schema.post_items.c.post_shortcode.in_(posts_statement)
        ).order_by(
            schema.posts.c.creation_time.desc(), schema.post_items.c.index.asc()
        )

        posts = []
        for result in await self.database.fetch_all(statement):
            item = PostItem(
                type=result['item_type'],
                duration=result['item_duration'],
                filename=result['item_filename'],
                thumb_image_filename=result['item_thumb_image_filename'],
            )
            if posts and posts[-1].shortcode == result['shortcode']:
                posts[-1].items.append(item)
            else:
                post = Post2(items=[item], **result)
                posts.append(post)

        statement = sa.select([sa.func.count()]).select_from(schema.posts)
        count = await self.database.fetch_val(statement)

        return PostListResult(posts=posts, limit=limit, offset=offset, count=count)

    async def delete(self, shortcode: str, index: Optional[int] = None):
        # find info about files to delete
        if index is not None:
            where_clause = sa.and_(
                schema.post_items.c.post_shortcode == shortcode,
                schema.post_items.c.index == index,
            )
        else:
            where_clause = schema.post_items.c.post_shortcode == shortcode
        list_statement = sa.select([
            schema.posts.c.owner_username,
            schema.post_items.c.type,
            schema.post_items.c.filename,
            schema.post_items.c.thumb_image_filename,
        ]).select_from(
            schema.posts.join(schema.post_items, schema.posts.c.shortcode == schema.post_items.c.post_shortcode)
        ).where(where_clause)

        # delete files
        for result in await self.database.fetch_all(list_statement):
            media_path = self.post_dir.joinpath(result['owner_username'], result['filename'])
            media_path.unlink(missing_ok=True)
            if result['thumb_image_filename']:
                thumb_path = self.thumb_images_dir.joinpath(result['owner_username'], result['filename'])
                thumb_path.unlink(missing_ok=True)


    async def create_from_shortcode(self, shortcode: str):
        """Create a post from a shortcode.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Post.from_shortcode
            post = await loop.run_in_executor(None, func, self.instaloader_context, shortcode)
            return await self.create_from_instaloader(post)
        except Exception:
            logger.warning(f'Failed to retrieved Post: {shortcode}')
            raise PostNotFound(shortcode)

    async def create_from_time_range(self, username: str, start: datetime, end: datetime):
        """Create posts from a profile within a time range.

        :param username: username of the profile to archive posts
        :param start: start of the time range to archive posts
        :param end: end of the time range to archive posts
        """

        # get the post iterator
        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            profile = await loop.run_in_executor(None, func, self.instaloader_context, username)
            post_iterator: instaloader.NodeIterator = await loop.run_in_executor(None, profile.get_posts)
        except instaloader.ProfileNotExistsException:
            logger.warning(f'Failed to create posts from time range. Profile {username} does not exist.')
            return

        while True:
            # fetch the next post
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
            except StopIteration:
                break

            # if post is later than the end date, that means we have yet to reach posts within the time range
            if post.date_utc >= end:
                continue

            # if post is earlier than the start date, that means we have iterated through posts within the time range
            if post.date_utc < start:
                break

            await self.create_from_instaloader(post)

    async def create_from_instaloader(self, post: instaloader.Post):
        """Create a post from a instaloader post object.

        :param post: a instaloader post object
        """

        post = Post.from_instaloader(post)

        # create profile if not exist
        profile_service = ProfileService(self.database, self.http_session)
        if not await profile_service.exists(post.owner_username):
            await profile_service.upsert(post.owner_username)

        # save post
        await self._download_image_video(post)
        await self._save_metadata(post)

        logger.info(
            f'Saved post {post.shortcode} of user {post.owner_username} '
            f'which contains {len(post.items)} item(s).'
        )
        return post

    async def _download_image_video(self, post: Post):
        """Download images and videos of a post.

        :param post: post metadata
        """

        dir_path = Path('posts').joinpath(post.owner_username)
        thumb_dir_path = Path('thumb_images').joinpath(post.owner_username)
        post_timestamp = (post.creation_time.timestamp(), post.creation_time.timestamp())
        post_filename = f'{post.creation_time.strftime("%Y-%m-%dT%H-%M-%S")}_[{post.shortcode}]'

        for index, item in enumerate(post.items):
            # save the image or video
            filename = f'{post_filename}_{index}' if len(post.items) > 1 else post_filename
            file_path = await self.save_media(item.url, dir_path, filename)
            item.filename = file_path.name
            os.utime(file_path, post_timestamp)

            # save thumb image path
            if item.thumb_url:
                file_path = await self.save_media(item.thumb_url, thumb_dir_path, filename)
                item.thumb_image_filename = file_path.name
                os.utime(file_path, post_timestamp)

    async def _save_metadata(self, post: Post):
        """Save metadata of a post.

        :param post: post metadata
        """

        async with self.database.transaction():
            values = {
                'shortcode': post.shortcode,
                'owner_username': post.owner_username,
                'creation_time': post.creation_time,
                'type': post.type.value,
                'caption': post.caption,
                'caption_hashtags': post.caption_hashtags,
                'caption_mentions': post.caption_mentions,
            }
            updates = values.copy()
            updates.pop('shortcode')
            statement = insert(schema.posts).values(**values)
            statement = statement.on_conflict_do_update(index_elements=[schema.posts.c.shortcode], set_=updates)
            await self.database.execute(statement)

            for item in post.items:
                values = {
                    'post_shortcode': post.shortcode,
                    'index': item.index,
                    'type': item.type.value,
                    'duration': item.duration,
                    'filename': item.filename,
                    'thumb_image_filename': item.thumb_image_filename,
                }
                updates = values.copy()
                updates.pop('post_shortcode')
                updates.pop('index')
                statement = insert(schema.post_items).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[schema.post_items.c.post_shortcode, schema.post_items.c.index],
                    set_=updates
                )
                await self.database.execute(statement)
