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
    latest_post_timestamp: Optional[datetime]  # timestamp of the latest post in the database
    last_archive_timestamp: Optional[datetime]  # timestamp of the last auto archive
    last_archive_latest_post_timestamp: Optional[datetime]  # timestamp of the latest known post found in last archive
    post_count: int = 0


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

                # get the timestamp that is used to stop auto archive
                stopping_timestamp = max(filter(lambda x: x is not None, [
                    auto_archive.latest_post_timestamp,
                    auto_archive.last_archive_latest_post_timestamp,
                    datetime.utcnow() - timedelta(days=7)
                ]))

                while True:
                    # fetch the next post
                    try:
                        post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
                    except StopIteration:
                        break

                    # break if post timestamp is earlier than or the same as the stopping timestamp
                    if stopping_timestamp >= post.date_utc:
                        break

                    # archive the post
                    await PostService(self.database, self.http_session).create_from_instaloader(post)
                    auto_archive.post_count += 1
                    if timestamp := auto_archive.last_archive_latest_post_timestamp:
                        auto_archive.last_archive_latest_post_timestamp = max(post.date_utc, timestamp)
                    else:
                        auto_archive.last_archive_latest_post_timestamp = post.date_utc

                # update last archive info of the profile
                statement = sa.update(schema.profiles) \
                    .where(schema.profiles.c.username == auto_archive.username) \
                    .values(
                    last_archive_timestamp=datetime.utcnow(),
                    last_archive_latest_post_timestamp=auto_archive.last_archive_latest_post_timestamp,
                )
                await self.database.execute(statement)

                message = f'Auto archive profile {auto_archive.username} -- {auto_archive.post_count} post(s) added.'
                logging.info(message)
                return auto_archive.username

    async def _find_next(self) -> Optional[AutoArchive]:
        """Find auto archive info of the next outdated profile.

        A profile is considered outdated when:
        - auto archive is set to true
        - the profile's last archive time is older than the OUTDATED_THRESHOLD or has never been updated

        :return: profile auto archive info
        """

        # get the next profile
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
        auto_archive = AutoArchive(latest_post_timestamp=None, **result)

        # get latest_post_timestamp
        statement = sa.select([
            sa.func.max(schema.posts.c.timestamp).label('max_timestamp')
        ]).select_from(schema.posts).where(schema.posts.c.username == auto_archive.username)
        result = await self.database.fetch_one(statement)
        auto_archive.latest_post_timestamp = result.get('max_timestamp')

        return auto_archive
