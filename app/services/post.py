import asyncio
import mimetypes
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
    async def create(self, shortcodes: [str], connection: sa.engine.Connection):
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
            await self.save_metadata(post, connection)
            await self.download_image_video(post)

            logger.info(
                f'Saved post {post.shortcode} of user {post.owner_username} '
                f'which contains {len(post.items)} item(s).'
            )

    def retrieve(self, shortcode: str) -> Optional[Post]:
        """Retrieve info about a single post from the Internet.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        try:
            post = instaloader.Post.from_shortcode(self.instaloader_context, shortcode)
            post_type = PostType.from_instagram(post.typename)

            if post_type == PostType.IMAGE:
                items = [PostItem(PostItemType.IMAGE, post.url)]
            elif post_type == PostType.VIDEO:
                items = [PostItem(PostItemType.VIDEO, post.video_url)]
            elif post_type == PostType.SIDECAR:
                items = [
                    PostItem(
                        PostItemType.VIDEO if node.is_video else PostItemType.IMAGE,
                        node.video_url if node.is_video else node.display_url
                    )
                    for node in post.get_sidecar_nodes()
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

                    # save file
                    profile_dir.mkdir(parents=True, exist_ok=True)
                    self._change_file_ownership(profile_dir)
                    with open(file_path, 'wb') as file:
                        data = await response.read()
                        file.write(data)
                        self._change_file_ownership(file_path)
