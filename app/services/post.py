import asyncio
import logging
import os
from pathlib import Path

import instaloader
from sqlalchemy.dialects.postgresql import insert

from services import schema
from services.base import BaseService
from services.entities import Post
from services.exceptions import PostNotFound
from services.profile import ProfileService

logger = logging.getLogger(__name__)


class PostService(BaseService):
    async def create_from_shortcode(self, shortcode: str):
        """Create and save a post from its shortcode.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        post = await self._retrieve(shortcode)

        # create profile if not exist
        profile_service = ProfileService(self.database, self.http_session)
        if not await profile_service.exists(post.owner_username):
            await profile_service.upsert(post.owner_username)

        await self._download_image_video(post)
        await self._save_metadata(post)

        logger.info(
            f'Saved post {post.shortcode} of user {post.owner_username} '
            f'which contains {len(post.items)} item(s).'
        )
        return post

    async def _retrieve(self, shortcode: str) -> Post:
        """Retrieve info about a single post from the Internet.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Post.from_shortcode
            post = await loop.run_in_executor(None, func, self.instaloader_context, shortcode)
            logger.debug(f'Retrieved Post: {shortcode}')
            return Post.from_instaloader(post)
        except Exception:
            logger.warning(f'Failed to retrieved Post: {shortcode}')
            raise PostNotFound(shortcode)

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
            file_name = f'{post_filename}_{index}' if len(post.items) > 1 else post_filename
            file_path = await self.save_media(item.url, dir_path, file_name)
            os.utime(file_path, post_timestamp)

            # save thumb image path
            if item.thumb_url:
                file_path = await self.save_media(item.thumb_url, thumb_dir_path, file_name)
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
                    'filename': item.filename,
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
