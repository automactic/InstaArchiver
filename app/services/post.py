import asyncio
import logging
import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path

import aiofiles
import aiohttp
import instaloader
import sqlalchemy
import yarl
from sqlalchemy.dialects.postgresql import insert

from services import schema
from services.entities import Post
from services.exceptions import PostNotFound
from services.profile import ProfileService

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self, connection: sqlalchemy.engine.Connection):
        self.connection = connection
        self.instaloader_context = instaloader.InstaloaderContext()
        self.data_dir = Path('/data')

        try:
            self.user_id = int(os.getenv('USER_ID'))
        except ValueError:
            self.user_id = None
        try:
            self.group_id = int(os.getenv('GROUP_ID'))
        except ValueError:
            self.group_id = None

    async def create_from_shortcode(self, shortcode: str):
        """Create and save a post from its shortcode.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        post = await self._retrieve(shortcode)

        # create profile if not exist
        profile_service = ProfileService(self.connection)
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

    def _set_file_ownership(self, path: Path):
        """Change ownership of the directory or file to a specific user id or group id.

        :param path: the directory or file path to change the ownership
        """

        if self.user_id or self.group_id:
            shutil.chown(path, self.user_id, self.group_id)

    @staticmethod
    def _set_file_access_modify_time(path: Path, creation_time: datetime):
        """Set file access time and modify time to post creation time.

        :param path: the file path to change access time and modify time
        :param creation_time: post creation time
        """

        timestamp = creation_time.timestamp()
        os.utime(path, (timestamp, timestamp))

    async def _download_image_video(self, post: Post):
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
                    self._set_file_ownership(profile_dir)
                    async with aiofiles.open(file_path, 'wb') as file:
                        data = await response.read()
                        await file.write(data)
                        self._set_file_ownership(file_path)
                        self._set_file_access_modify_time(file_path, post.creation_time)

    async def _save_metadata(self, post: Post):
        """Save metadata of a post.

        :param post: post metadata
        """

        with self.connection.begin():
            values = {
                'shortcode': post.shortcode,
                'owner_username': post.owner_username,
                'creation_time': post.creation_time,
                'type': post.type.value,
                'caption': post.caption,
            }
            updates = values.copy()
            updates.pop('shortcode')
            statement = insert(schema.posts, bind=self.connection.engine).values(**values)
            statement = statement.on_conflict_do_update(index_elements=[schema.posts.c.shortcode], set_=updates)
            self.connection.execute(statement)

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
                statement = insert(schema.post_items, bind=self.connection.engine).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[schema.post_items.c.post_shortcode, schema.post_items.c.index],
                    set_=updates
                )
                self.connection.execute(statement)
