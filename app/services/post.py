import asyncio
import mimetypes
from pathlib import Path
from typing import Optional

import aiohttp
import instaloader

from services import Post, PostItem, PostItemType, PostType
from .base import BaseService


class PostService(BaseService):
    def __init__(self):
        super(PostService, self).__init__()
        self.instaloader_context = instaloader.InstaloaderContext()
        self.data_dir = Path('/data')

    async def create(self, shortcodes: [str]):
        loop = asyncio.get_running_loop()
        for shortcode in shortcodes:
            post = await loop.run_in_executor(None, self.get_post, shortcode)
            if not post:
                continue
            await self.download_post(post)
            print(post)

    def get_post(self, shortcode: str) -> Optional[Post]:
        """Retrieve info about a single Instagram post from the Internet.

        :param shortcode: shortcode of the Instagram post
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

    async def download_post(self, post: Post):
        """Download images and videos of a post.

        :param post: the post to download
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
