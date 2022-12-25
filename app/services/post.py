import asyncio
import logging
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import instaloader
import pydantic
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.posts import Post, PostItem, PostType, PostItemType, PostListResult, PostArchiveRequest
from services import schema
from services.base import BaseService
from services.profile import ProfileService

logger = logging.getLogger(__name__)


@dataclass
class DownloadTask:
    url: str
    thumb_url: Optional[str] = None


class PostService(BaseService):
    async def list(
        self,
        offset: int = 0,
        limit: int = 10,
        username: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> PostListResult:
        """List posts.

        :param offset: the number of posts to skip
        :param limit: the number of posts to fetch
        :param username: username of post owner to filter
        :param start_time: the start of creation time to filter posts
        :param end_time: the end of creation time to filter posts
        :return: the list query result
        """

        # build base query
        condition = []
        if username:
            condition.append(schema.posts.c.username == username)
        if start_time:
            start_time = datetime.utcfromtimestamp(start_time.timestamp())
            condition.append(schema.posts.c.timestamp >= start_time)
        if end_time:
            end_time = datetime.utcfromtimestamp(end_time.timestamp())
            condition.append(schema.posts.c.timestamp < end_time)
        base_query = schema.posts.select().where(sa.and_(*condition)).cte('base_query')

        # build post and count query
        posts_query = base_query.select().order_by(base_query.c.timestamp.desc()) \
            .offset(offset).limit(limit).cte('posts_query')
        count_query = sa.select(sa.func.count().label('total_count')).select_from(base_query).cte('count_query')

        # build final query
        query = sa.select(
            posts_query.c.shortcode.label('shortcode'),
            posts_query.c.username.label('username'),
            posts_query.c.timestamp.label('timestamp'),
            posts_query.c.type.label('type'),
            posts_query.c.caption.label('caption'),
            posts_query.c.caption_hashtags.label('caption_hashtags'),
            posts_query.c.caption_mentions.label('caption_mentions'),
            schema.post_items.c.index.label('item_index'),
            schema.post_items.c.type.label('item_type'),
            schema.post_items.c.duration.label('item_duration'),
            schema.post_items.c.filename.label('item_filename'),
            schema.post_items.c.thumb_image_filename.label('item_thumb_image_filename'),
            count_query.c.total_count.label('total_count'),
        ).select_from(
            posts_query.outerjoin(
                schema.post_items,
                posts_query.c.shortcode == schema.post_items.c.shortcode,
                full=False,
            ).outerjoin(count_query, sa.sql.true(), full=True)
        )

        # format the results
        posts, count = [], 0
        for result in await self.database.fetch_all(query):
            count = result['total_count']
            if not posts or posts[-1].shortcode != result['shortcode']:
                try:
                    post = Post(items=[], **dict(result))
                    post.timestamp = post.timestamp.replace(tzinfo=timezone.utc)
                    posts.append(post)
                except pydantic.error_wrappers.ValidationError:
                    continue
            try:
                item = PostItem(
                    index=result['item_index'],
                    type=result['item_type'],
                    duration=result['item_duration'],
                    filename=result['item_filename'],
                    thumb_image_filename=result['item_thumb_image_filename'],
                )
                posts[-1].items.append(item)
            except pydantic.error_wrappers.ValidationError:
                continue

        return PostListResult(posts=posts, limit=limit, offset=offset, count=count)

    async def exists(self, shortcode: str) -> bool:
        """Check if a post exists.

        :param shortcode: shortcode of the post to check
        :return: if the post exists
        """

        statement = sa.select([schema.posts.c.shortcode]).where(schema.posts.c.shortcode == shortcode)
        exists_statement = sa.select([sa.exists(statement)])
        return await self.database.fetch_val(query=exists_statement)

    async def delete(self, shortcode: str, index: Optional[int] = None):
        """Delete post and post items

        :param shortcode: the shortcode of the post to delete
        :param index: index of the post item to delete
        """

        async with self.database.transaction():
            # find info about post items
            list_statement = sa.select([
                schema.posts.c.username,
                schema.post_items.c.index,
                schema.post_items.c.type,
                schema.post_items.c.filename,
                schema.post_items.c.thumb_image_filename,
            ]).select_from(
                schema.posts.join(schema.post_items, schema.posts.c.shortcode == schema.post_items.c.shortcode)
            ).where(schema.post_items.c.shortcode == shortcode)
            post_items = [item for item in await self.database.fetch_all(list_statement)]

            # delete files
            for item in post_items:
                if index is not None and item['index'] != index:
                    continue
                if filename := item['filename']:
                    self.delete_file(self.post_dir, item['username'], filename)
                if thumb_image_filename := item['thumb_image_filename']:
                    self.delete_file(self.thumb_images_dir, item['username'], thumb_image_filename)

            # delete post(if post has only one item left) and post item records
            if index is not None:
                where_clause = sa.and_(
                    schema.post_items.c.shortcode == shortcode,
                    schema.post_items.c.index == index,
                )
            else:
                where_clause = schema.post_items.c.shortcode == shortcode
            delete_statement = sa.delete(schema.post_items).where(where_clause)
            await self.database.execute(delete_statement)
            if len(post_items) == 1:
                delete_statement = sa.delete(schema.posts).where(schema.posts.c.shortcode == shortcode)
                await self.database.execute(delete_statement)

    async def create_from_shortcode(self, shortcode: str) -> Post:
        """Create a post from a shortcode.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Post.from_shortcode
            post = await loop.run_in_executor(None, func, self.instaloader.context, shortcode)
            return await self.create_from_instaloader(post)
        except Exception:
            logger.warning(f'Failed to retrieved Post: {shortcode}')

    async def create_from_time_range(self, request: PostArchiveRequest.FromTimeRange):
        """Create posts from a profile within a time range.

        :param request: post archive request
        """

        # get the post iterator
        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            profile = await loop.run_in_executor(None, func, self.instaloader.context, request.username)
            post_iterator: instaloader.NodeIterator = await loop.run_in_executor(None, profile.get_posts)
        except instaloader.ProfileNotExistsException:
            logger.warning(f'Failed to create posts from time range. Profile {request.username} does not exist.')
            return

        count = 0
        while True:
            # fetch the next post
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
            except StopIteration:
                logger.debug('Unable to get the next post.')
                break

            # skip pinned posts
            if post.is_pinned:
                continue

            # if post is later than the end date, that means we have yet to reach posts within the time range
            if post.date_utc >= request.end:
                logger.debug(f'Post date {post.date_utc} is later than the end date.')
                continue

            # if post is earlier than the start date, that means we have iterated through posts within the time range
            if post.date_utc < request.start:
                logger.debug(f'Post date {post.date_utc} is earlier than the start date.')
                break

            # save post
            await self.create_from_instaloader(post)
            count += 1

            # sleep for a random amount of time
            max_sleep = os.environ.get('MAX_SLEEP', 60)
            await asyncio.sleep(random.randint(0, max_sleep))
        logger.info(
            f'Saved {count} post(s) for profile {request.username} from {request.start} to {request.end}.'
        )

    async def archive_saved(self, count: Optional[int] = None):
        """Archive saved posts in the account that is currently logged in.

        :param count: number of most recent posts to archive before stopping
        """

        # get the post iterator
        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            profile = await loop.run_in_executor(None, func, self.instaloader.context, self.instagram_username)
            post_iterator: instaloader.NodeIterator = await loop.run_in_executor(None, profile.get_saved_posts)
        except instaloader.ProfileNotExistsException:
            logger.warning(f'Failed to create posts from saved. Profile {self.instagram_username} does not exist.')
            return

        total_counter = 0
        archived_counter = 0
        while True:
            # fetch the next post
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
                total_counter += 1
                logger.debug(f'Fetched post: {post.shortcode}')
            except StopIteration:
                break

            # if the current post already exists,
            # end the loop if not trying to archive certain amount of most recent posts
            if await self.exists(post.shortcode):
                if count is None:
                    break
                else:
                    continue

            # archive unsaved post and increment the counter
            await self.create_from_instaloader(post)
            archived_counter += 1

            # sleep for a random amount of time
            max_sleep = os.environ.get('MAX_SLEEP', 60)
            await asyncio.sleep(random.randint(0, max_sleep))

            # break if already iterated through enough posts
            if count and total_counter >= count:
                break

        logger.info(f'Archived {archived_counter} saved post(s).')

    async def create_from_instaloader(self, post: instaloader.Post) -> Post:
        """Create a post from a instaloader post object.

        :param post: a instaloader post object
        """

        # figure out post_type, items and download_tasks
        if post.typename == 'GraphImage':
            post_type = PostType.IMAGE
            items = [PostItem(index=0, type=PostItemType.IMAGE)]
            download_tasks = [DownloadTask(url=post.url)]
        elif post.typename == 'GraphVideo':
            post_type = PostType.VIDEO
            items = [PostItem(index=0, type=PostItemType.VIDEO, duration=post.video_duration)]
            download_tasks = [DownloadTask(url=post.video_url, thumb_url=post.url)]
        elif post.typename == 'GraphSidecar':
            post_type = PostType.SIDECAR
            items, download_tasks = [], []
            for index, node in enumerate(post.get_sidecar_nodes()):
                post_item = PostItem(index=index, type=PostItemType.VIDEO if node.is_video else PostItemType.IMAGE)
                download_task = DownloadTask(
                    url=node.video_url if node.is_video else node.display_url,
                    thumb_url=node.display_url if node.is_video else None,
                )
                items.append(post_item)
                download_tasks.append(download_task)
        else:
            post_type = None
            items, download_tasks = [], []

        # convert instaloader post to Post object
        post = Post(
            shortcode=post.shortcode,
            username=post.owner_username,
            timestamp=post.date_utc,
            type=post_type,
            caption=post.caption,
            caption_hashtags=post.caption_hashtags,
            caption_mentions=post.caption_mentions,
            items=[],
        )

        # create profile if not exist
        profile_service = ProfileService(self.database, self.http_session)
        if not await profile_service.exists(post.username):
            await profile_service.upsert(post.username)

        # download image and videos
        post_filename = f'{post.timestamp.strftime("%Y-%m-%dT%H-%M-%S")}_[{post.shortcode}]'
        for item, download_task in zip(items, download_tasks):
            filename = f'{post_filename}_{item.index}' if len(items) > 1 else post_filename
            file_path = self._download(
                download_task.url,
                self.post_dir.joinpath(post.username),
                filename,
                post.timestamp
            )
            item.filename = file_path.name
            if download_task.thumb_url:
                file_path = self._download(
                    download_task.thumb_url,
                    self.thumb_images_dir.joinpath(post.username),
                    filename,
                    post.timestamp,
                )
                item.thumb_image_filename = file_path.name

        # upsert the post entity
        post.items = items
        await self._upsert(post)

        logger.info(
            f'Saved post {post.shortcode} of user {post.username} '
            f'which contains {len(post.items)} item(s).'
        )
        return post

    async def _upsert(self, post: Post):
        """Create or update a post.

        :param post: post metadata
        """

        async with self.database.transaction():
            values = {
                'shortcode': post.shortcode,
                'username': post.username,
                'timestamp': post.timestamp,
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
                    'shortcode': post.shortcode,
                    'index': item.index,
                    'type': item.type.value,
                    'duration': item.duration,
                    'filename': item.filename,
                    'thumb_image_filename': item.thumb_image_filename,
                }
                updates = values.copy()
                updates.pop('shortcode')
                updates.pop('index')
                statement = insert(schema.post_items).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[schema.post_items.c.shortcode, schema.post_items.c.index],
                    set_=updates
                )
                await self.database.execute(statement)
