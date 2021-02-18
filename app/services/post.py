import asyncio
import logging
from typing import Optional

import instaloader

from services.entities import Post

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self):
        self.instaloader_context = instaloader.InstaloaderContext()

    async def create_from_shortcode(self, shortcode: str):
        post = await self.retrieve(shortcode)

    async def retrieve(self, shortcode: str) -> Optional[Post]:
        """Retrieve info about a single post from the Internet.

        :param shortcode: shortcode of a single post
        :return: post metadata
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Post.from_shortcode
            post = await loop.run_in_executor(None, func, self.instaloader_context, shortcode)
            logger.debug('Retrieved Post', extra={'shortcode': shortcode})
            return Post.from_instaloader(post)
        except Exception:
            return None
