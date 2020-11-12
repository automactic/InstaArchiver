import asyncio
import mimetypes
from datetime import datetime
from logging import getLogger
from typing import Optional

import aiofiles
import aiohttp
import instaloader
import sqlalchemy as sa
import yarl
from sqlalchemy.dialects.postgresql import insert

from . import schema
from .base import BaseService
from .entities import Post
from .profile import ProfileService

logger = getLogger(__name__)


class PostService(BaseService):
    async def create_from_shortcodes(self, shortcodes: [str], connection: sa.engine.Connection):
        """Create posts from shortcodes.

        :param shortcodes: shortcodes of the post to create
        :param connection: a database connection
        """

        loop = asyncio.get_running_loop()
        profile_service = ProfileService()
        for shortcode in shortcodes:
            # fetch post metadata
            post = await loop.run_in_executor(None, self.retrieve, shortcode)
            if not post:
                continue

            # make sure profile exists
            profile_exists = await loop.run_in_executor(None, profile_service.exists, post.owner_username, connection)
            if not profile_exists:
                await profile_service.create(post.owner_username, connection)

            # save post metadata and download images & videos
            await self.download_image_video(post)
            await self.save_metadata(post, connection)

            logger.info(
                f'Saved post {post.shortcode} of user {post.owner_username} '
                f'which contains {len(post.items)} item(s).'
            )

    async def create_from_time_range(
            self, username: str, start_time: datetime, end_time: datetime, connection: sa.engine.Connection
    ):
        """Create posts from a username and a time range.

        :param username:
        :param start_time:
        :param end_time:
        :param connection: a database connection
        """

        loop = asyncio.get_running_loop()

        # make sure profile exists
        profile_service = ProfileService()
        profile = await loop.run_in_executor(None, profile_service.retrieve, username)
        if not profile:
            logger.error(f'Unable to create posts from time range: profile {username} does not exist.')
            return
        if not await loop.run_in_executor(None, profile_service.exists, username, connection):
            await loop.run_in_executor(None, profile_service.upsert, profile, connection)

        # save posts metadata and download images & videos
        counter = 0
        while True:
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, profile.post_iterator)
                if post.date > end_time:
                    continue
                elif post.date > start_time:
                    post: Post = Post.from_instaloader(post)
                    await self.download_image_video(post)
                    await self.save_metadata(post, connection)
                    counter += 1
                    logger.info(
                        f'Saved post {post.shortcode} of user {post.owner_username} '
                        f'which contains {len(post.items)} item(s).'
                    )
                else:
                    break
            except StopIteration:
                break
        logger.info(
            f'Saved {counter} post(s) of user {username} '
            f'between {start_time.isoformat()} and {end_time.isoformat()}.'
        )

    def retrieve(self, shortcode: str) -> Optional[Post]:
        """Retrieve info about a single post from the Internet.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        try:
            post = instaloader.Post.from_shortcode(self.instaloader_context, shortcode)
            return Post.from_instaloader(post)
        except Exception:
            return None

    async def download_image_video(self, post: Post):
        """Download images and videos of a post.

        :param post: post metadata
        """

        post_filename = f'{post.creation_time.strftime("%Y-%m-%dT%H-%M-%S")}_[{post.shortcode}]'
        async with aiohttp.ClientSession() as session:
            for index, item in enumerate(post.items):
                async with session.get(yarl.URL(item.url, encoded=True)) as response:
                    # get post item filename
                    if len(post.items) > 1:
                        post_item_filename = f'{post_filename}_{index}'
                    else:
                        post_item_filename = post_filename

                    # get extension
                    extension = mimetypes.guess_extension(response.content_type)
                    if not extension:
                        return

                    # assemble post item file path
                    profile_dir = self.data_dir.joinpath(post.owner_username)
                    file_path = profile_dir.joinpath(post_item_filename).with_suffix(extension)
                    item.filename = file_path.name

                    # save file
                    profile_dir.mkdir(parents=True, exist_ok=True)
                    self._change_file_ownership(profile_dir)
                    async with aiofiles.open(file_path, 'wb') as file:
                        data = await response.read()
                        await file.write(data)
                        self._change_file_ownership(file_path)
                        self._set_file_access_modify_time(file_path, post.creation_time)

    @staticmethod
    async def save_metadata(post: Post, connection: sa.engine.Connection):
        """Save metadata of a post.

        :param post: post metadata
        :param connection: a database connection
        """

        with connection.begin():
            values = {
                'shortcode': post.shortcode,
                'owner_username': post.owner_username,
                'creation_time': post.creation_time,
                'type': post.type.value,
                'caption': post.caption,
            }
            updates = values.copy()
            updates.pop('shortcode')
            statement = insert(schema.posts, bind=connection.engine).values(**values)
            statement = statement.on_conflict_do_update(index_elements=[schema.posts.c.shortcode], set_=updates)
            connection.execute(statement)

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
                statement = insert(schema.post_items, bind=connection.engine).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[schema.post_items.c.post_shortcode, schema.post_items.c.index],
                    set_=updates
                )
                connection.execute(statement)
