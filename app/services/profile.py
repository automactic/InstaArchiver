import asyncio
import logging
from pathlib import Path

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from services import schema
from services.base import BaseService
from services.entities import Profile, ProfileDetail, ProfileListResult, PostsSummary
from typing import Optional
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
            'biography': profile.biography,
            'auto_update': False,
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

        statement = schema.profiles.select(offset=offset, limit=limit)
        profiles = [Profile(**profile) for profile in await self.database.fetch_all(query=statement)]

        statement = sa.select([sa.func.count()]).select_from(schema.profiles)
        count = await self.database.fetch_val(query=statement)

        return ProfileListResult(profiles=profiles, limit=limit, offset=offset, count=count)

    async def get(self, username: str) -> Optional[ProfileDetail]:
        """Get a single profile.

        :param username: the username of the profile to get.
        :return: the profile query result
        """

        statement = sa.select([
            schema.profiles.c.username,
            schema.profiles.c.full_name,
            schema.profiles.c.biography,
            schema.profiles.c.auto_update,
            schema.profiles.c.last_update,
            schema.profiles.c.image_filename,
            sa.func.count(schema.posts.c.shortcode).label('post_count'),
            sa.func.min(schema.posts.c.creation_time).label('earliest_time'),
            sa.func.max(schema.posts.c.creation_time).label('latest_time'),
        ]).select_from(
            schema.profiles.join(
                schema.posts, schema.profiles.c.username == schema.posts.c.owner_username
            )
        ).where(schema.profiles.c.username == username).group_by(schema.profiles.c.username)
        result = await self.database.fetch_one(query=statement)

        profile_detail = ProfileDetail(
            username=result['username'],
            full_name=result['full_name'],
            biography=result['biography'],
            auto_update=result['auto_update'],
            last_update=result['last_update'],
            image_filename=result['image_filename'],
            posts=PostsSummary(
                count=result['post_count'],
                earliest_time=result['earliest_time'],
                latest_time=result['latest_time'],
            )
        )
        return profile_detail
