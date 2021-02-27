import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import instaloader
import sqlalchemy as sa
import sqlalchemy.sql.operators

from services import schema, PostService
from .base import BaseService

logger = logging.getLogger(__name__)


class AutoArchiveService(BaseService):
    OUTDATED_THRESHOLD = timedelta(minutes=15)

    async def update_profiles(self):
        """Catching up new posts of all outdated profiles."""

        while True:
            username = await self.update_one_profile()
            if not username:
                break

    async def update_one_profile(self) -> Optional[str]:
        """Catching up new posts of one profile.

        :return: username of the profile that got updated
        """

        loop = asyncio.get_running_loop()
        async with self.database.transaction():
            if username := await self._find_next_profile():
                func = instaloader.Profile.from_username
                profile = await loop.run_in_executor(None, func, self.instaloader_context, username)
                post_iterator: instaloader.NodeIterator = await loop.run_in_executor(None, profile.get_posts)

                latest_post_creation_time = await self._find_latest_post_creation_time(username)
                while True:
                    # fetch the next post
                    try:
                        post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
                    except StopIteration:
                        break

                    # break if post is earlier than or the same as the latest archived post
                    if latest_post_creation_time and latest_post_creation_time >= post.date_utc:
                        break

                    # archive the post
                    await PostService(self.database, self.http_session).create_from_instaloader(post)

                await self._set_last_scan_timestamp(username)
                return username

    async def _find_next_profile(self) -> Optional[str]:
        """Find username of the next outdated profile to archive.

        A profile is considered outdated when:
        - auto update is set to true
        - the profile was last updated OUTDATED_THRESHOLD ago or has never been updated

        :return: username of the profile to update
        """

        statement = sa.select([schema.profiles.c.username], for_update=True) \
            .select_from(schema.profiles) \
            .where(sa.and_(
                sa.sql.operators.eq(schema.profiles.c.auto_archive, True),
                sa.or_(
                    schema.profiles.c.last_scan < datetime.utcnow() - self.OUTDATED_THRESHOLD,
                    sa.sql.operators.eq(schema.profiles.c.last_scan, None),
                )
            )) \
            .order_by(schema.profiles.c.last_scan.desc().nullsfirst()) \
            .limit(1)
        result = await self.database.fetch_one(statement)
        return result.get('username')

    async def _find_latest_post_creation_time(self, username: str) -> Optional[datetime]:
        """Find creation time of the latest post that belongs to a profile.

        :param username: username of the profile
        :return: creation time of the latest post
        """

        statement = sa.select([
            sa.func.max(schema.posts.c.creation_time).label('max_creation_time')
        ]).select_from(schema.posts).where(schema.posts.c.owner_username == username)
        result = await self.database.fetch_one(statement)
        return result.get('max_creation_time')

    async def _set_last_scan_timestamp(self, username: str):
        """Update last_scan column of a profile to utc now.

        :param username: username of the profile to perform update
        """

        statement = sa.update(schema.profiles)\
            .where(schema.profiles.c.username == username)\
            .values(last_scan=datetime.utcnow())
        await self.database.execute(statement)
