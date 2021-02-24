import asyncio
import logging
import aiohttp
import instaloader
import sqlalchemy as sa
from databases import Database
from sqlalchemy.dialects.postgresql import insert

from services import schema
from services.base import BaseService
from services.entities import Profile, ProfileListResult
from pathlib import Path
logger = logging.getLogger(__name__)


class ProfileService(BaseService):
    def __init__(self, database: Database, http_session: aiohttp.ClientSession):
        super().__init__(database, http_session)

        self.profile_image_dir = self.media_dir.joinpath('profile_image')
        self.database = database
        self.instaloader_context = instaloader.InstaloaderContext()

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
        await self.save_media(profile.profile_pic_url, Path('profile_image'), profile.username)

        # upsert profile
        values = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
            'auto_update': False,
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
