import asyncio
from typing import Optional

import instaloader

from services import Post, PostItem, PostItemType, PostType


class PostService:
    def __init__(self):
        self.instaloader_context = instaloader.InstaloaderContext()

    async def create(self, shortcode: str):
        loop = asyncio.get_running_loop()
        post = await loop.run_in_executor(None, self.get_post, shortcode)
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
                items = [PostItem(PostItemType.VIDEO, post.url)]
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
                created=post.date,
                type=PostType.from_instagram(post.typename),
                caption=post.caption,
                items=items,
            )
        except Exception:
            return None
