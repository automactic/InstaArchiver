import asyncio
import mimetypes
from datetime import datetime
from logging import getLogger
from typing import Optional

import aiohttp
import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from . import schema
from .base import BaseService
from .entities import Post, PostItem, PostItemType, PostType
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
        profile = await loop.run_in_executor(None, profile_service.get, username, connection)
        if not profile:
            profile = await profile_service.create(username, connection)
        if not profile:
            logger.error(f'Unable to create posts from time range: profile {username} does not exist.')
            return

    def retrieve(self, shortcode: str) -> Optional[Post]:
        """Retrieve info about a single post from the Internet.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        try:
            post = instaloader.Post.from_shortcode(self.instaloader_context, shortcode)
            post_type = PostType.from_instagram(post.typename)

            if post_type == PostType.IMAGE:
                items = [PostItem(type=PostItemType.IMAGE, url=post.url)]
            elif post_type == PostType.VIDEO:
                items = [PostItem(type=PostItemType.VIDEO, url=post.video_url)]
            elif post_type == PostType.SIDECAR:
                items = [
                    PostItem(
                        type=PostItemType.VIDEO if node.is_video else PostItemType.IMAGE,
                        index=index,
                        url=node.video_url if node.is_video else node.display_url
                    )
                    for index, node in enumerate(post.get_sidecar_nodes())
                ]
            else:
                items = []

            return Post(
                shortcode=post.shortcode,
                owner_username=post.owner_username,
                creation_time=post.date_utc,
                type=PostType.from_instagram(post.typename),
                caption=post.caption,
                items=items,
            )
        except Exception:
            return None

    async def download_image_video(self, post: Post):
        """Download images and videos of a post.

        :param post: post metadata
        """

        post_filename = f'{post.creation_time.strftime("%Y-%m-%dT%H-%M-%S")}_[{post.shortcode}]'
        async with aiohttp.ClientSession() as session:
            for index, item in enumerate(post.items):
                async with session.get(item.url) as response:
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
                    with open(file_path, 'wb') as file:
                        data = await response.read()
                        file.write(data)
                        self._change_file_ownership(file_path)

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
