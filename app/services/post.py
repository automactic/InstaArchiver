import asyncio
import logging
from typing import Optional

import instaloader
import sqlalchemy.ext.asyncio

from services.entities import Post
from services.profile import ProfileService

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self, connection: sqlalchemy.ext.asyncio.AsyncConnection):
        self.connection = connection
        self.instaloader_context = instaloader.InstaloaderContext()

    async def create_from_shortcode(self, shortcode: str):
        post = await self.retrieve(shortcode)

        # create profile if not exist
        profile_service = ProfileService(self.connection)
        profile_exists = await profile_service.exists(post.owner_username)
        if not profile_exists:
            await profile_service.upsert(post.owner_username)

    async def retrieve(self, shortcode: str) -> Optional[Post]:
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
            return None
