import asyncio
import logging
from datetime import timezone
from pathlib import Path
from typing import Optional

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.profiles import Profile, PostsSummary, ProfileDetail, ProfileListResult, ProfileUpdates
from services import schema
from services.base import BaseService

logger = logging.getLogger(__name__)


class ProfileService(BaseService):
    async def upsert(self, username: str):
        """Create or update a profile.

        :param username: username of the profile to create or update
        """

        # fetch profile
        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            profile = await loop.run_in_executor(None, func, self.instaloader_context, username)
        except instaloader.ProfileNotExistsException:
            logger.warning(f'Profile does not exist: {username}')
            return

        # save profile image
        image_path = await self.save_media(profile.profile_pic_url, Path('profile_images'), profile.username)

        # upsert profile
        values = {
            'username': profile.username,
            'full_name': profile.full_name,
            'display_name': profile.full_name,
            'biography': profile.biography,
            'auto_archive': False,
            'image_filename': image_path.parts[-1]
        }
        updates = values.copy()
        updates.pop('username')
        statement = insert(schema.profiles) \
            .values(**values) \
            .on_conflict_do_update(index_elements=[schema.profiles.c.username], set_=updates)
        await self.database.execute(statement)
        logger.info(f'Created Profile: {username}')

    async def exists(self, username: str) -> bool:
        """Check if a profile exists.

        :param username: username of the profile to check
        :return: if the profile exists
        """

        statement = sa.select([schema.profiles.c.username]).where(schema.profiles.c.username == username)
        exists_statement = sa.select([sa.exists(statement)])
        return await self.database.fetch_val(query=exists_statement)

    async def list(self, offset: int = 0, limit: int = 100) -> ProfileListResult:
        """List profiles.

        :param offset: the number of profiles to skip
        :param limit: the number of profiles to fetch
        :return: the list query result
        """

        statement = schema.profiles.select(offset=offset, limit=limit).order_by(schema.profiles.c.username)
        profiles = [Profile(**profile) for profile in await self.database.fetch_all(statement)]

        statement = sa.select([sa.func.count()]).select_from(schema.profiles)
        count = await self.database.fetch_val(statement)

        return ProfileListResult(profiles=profiles, limit=limit, offset=offset, count=count)

    async def get(self, username: str) -> Optional[ProfileDetail]:
        """Get a single profile.

        :param username: the username of the profile to get.
        :return: the profile query result
        """

        statement = sa.select([
            schema.profiles.c.username,
            schema.profiles.c.full_name,
            schema.profiles.c.display_name,
            schema.profiles.c.biography,
            schema.profiles.c.image_filename,
            schema.profiles.c.auto_archive,
            schema.profiles.c.last_archive_timestamp,
            sa.func.count(schema.posts.c.shortcode).label('post_count'),
            sa.func.min(schema.posts.c.timestamp).label('earliest_timestamp'),
            sa.func.max(schema.posts.c.timestamp).label('latest_timestamp'),
        ]).select_from(
            schema.profiles.join(
                schema.posts, schema.profiles.c.username == schema.posts.c.username
            )
        ).where(schema.profiles.c.username == username).group_by(schema.profiles.c.username)
        result = await self.database.fetch_one(query=statement)

        if result:
            return ProfileDetail(
                username=result['username'],
                full_name=result['full_name'],
                display_name=result['display_name'],
                biography=result['biography'],
                image_filename=result['image_filename'],
                auto_archive=result['auto_archive'],
                last_archive_timestamp=result['last_archive_timestamp'],
                posts=PostsSummary(
                    count=result['post_count'],
                    earliest_timestamp=result['earliest_timestamp'].replace(tzinfo=timezone.utc),
                    latest_timestamp=result['latest_timestamp'].replace(tzinfo=timezone.utc),
                )
            )
        else:
            return None

    async def update(self, username: str, updates: ProfileUpdates):
        """Update a profile

        :param username: username of the profile to update
        :param updates: the updates to perform
        """

        updates = {key: value for key, value in updates if value is not None}
        if not updates:
            return
        statement = sa.update(schema.profiles) \
            .where(schema.profiles.c.username == username) \
            .values(**updates)
        await self.database.execute(statement)
