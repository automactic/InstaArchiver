import asyncio
import logging

import instaloader
import sqlalchemy as sa
import sqlalchemy.ext.asyncio
from sqlalchemy.dialects.postgresql import insert

from services import schema

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, connection: sqlalchemy.ext.asyncio.AsyncConnection):
        self.connection = connection
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

        # upsert profile
        values = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
        }
        updates = values.copy()
        updates.pop('username')
        statement = insert(schema.profiles, bind=self.connection.engine) \
            .values(**values) \
            .on_conflict_do_update(index_elements=[schema.profiles.c.username], set_=updates)
        print(statement)
        result = await self.connection.execute(statement)
        print(result.fetchone())

        logger.info(f'Created Profile: {username}')

    async def exists(self, username: str) -> bool:
        """Check if a profile exists.

        :param username: username of the profile to check
        :return: if the profile exists
        """

        statement = schema.profiles.select().where(schema.profiles.c.username == username)
        exists_statement = sa.select([sa.exists(statement)])
        result = await self.connection.execute(exists_statement)
        return result.scalar()
