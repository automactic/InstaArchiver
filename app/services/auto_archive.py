import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import instaloader
import sqlalchemy as sa
import sqlalchemy.sql.operators

from services import schema
from .base import BaseService
from .post import PostService

logger = logging.getLogger(__name__)


@dataclass
class AutoArchive:
    username: str
    auto_archive: bool
    last_archive_timestamp: Optional[datetime]
    last_archive_latest_post_timestamp: Optional[datetime]


class AutoArchiveService(BaseService):
    OUTDATED_THRESHOLD = timedelta(hours=3)

    async def update_profiles(self):
        """Catching up new posts of all outdated profiles."""

        while True:
            username = await self._update_next()
            if not username:
                break

    async def _update_next(self) -> Optional[str]:
        """Catching up new posts of the next profile.

        :return: username of the profile that got updated, None if no profile needs to be updated
        """

        loop = asyncio.get_running_loop()
        async with self.database.transaction():
            if auto_archive := await self._find_next():
                func = instaloader.Profile.from_username
                profile = await loop.run_in_executor(None, func, self.instaloader_context, auto_archive.username)

                post_iterator: instaloader.NodeIterator = await loop.run_in_executor(None, profile.get_posts)
                latest_post_creation_time = await self._find_latest_post_creation_time(auto_archive.username)
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

                await self._set_last_archive_timestamp(auto_archive.username)
                return auto_archive.username

    async def _find_next(self) -> Optional[AutoArchive]:
        """Find auto archive info of the next outdated profile.

        A profile is considered outdated when:
        - auto archive is set to true
        - the profile's last archive time is older than the OUTDATED_THRESHOLD or has never been updated

        :return: profile auto archive info
        """

        where_clause = sa.and_(
            sa.sql.operators.eq(schema.profiles.c.auto_archive, True),
            sa.or_(
                schema.profiles.c.last_archive_timestamp < datetime.utcnow() - self.OUTDATED_THRESHOLD,
                sa.sql.operators.eq(schema.profiles.c.last_archive_timestamp, None),
            )
        )
        statement = sa.select([
            schema.profiles.c.username,
            schema.profiles.c.auto_archive,
            schema.profiles.c.last_archive_timestamp,
            schema.profiles.c.last_archive_latest_post_timestamp,
        ], for_update=True) \
            .select_from(schema.profiles) \
            .where(where_clause) \
            .order_by(schema.profiles.c.last_archive_timestamp.desc().nullsfirst()) \
            .limit(1)
        result = await self.database.fetch_one(statement)
        return AutoArchive(**result)

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

    async def _set_last_archive_timestamp(self, username: str):
        """Update last_archive_timestamp column of a profile to utc now.

        :param username: username of the profile to perform update
        """

        statement = sa.update(schema.profiles) \
            .where(schema.profiles.c.username == username) \
            .values(last_archive_timestamp=datetime.utcnow())
        await self.database.execute(statement)
