import asyncio
from logging import getLogger
from typing import Optional

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from . import schema
from .base import BaseService
from .entities import Profile

logger = getLogger(__name__)


class ProfileService(BaseService):
    async def create(self, username: str, connection: sa.engine.Connection):
        """Create a profile from username.

        :param username: username of the profile
        :param connection: a database connection
        """

        loop = asyncio.get_running_loop()

        # fetch profile metadata
        profile = await loop.run_in_executor(None, self.retrieve, username)
        if not profile:
            return

        # save profile metadata
        await loop.run_in_executor(None, self.upsert, profile, connection)

        logger.info(f'Saved profile info {profile.username}.')

    def upsert(self, profile: Profile, connection: sa.engine.Connection):
        """Create or update a profile.

        :param profile: profile metadata
        :param connection: a database connection
        """

        values = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
        }
        updates = values.copy()
        updates.pop('username')
        statement = insert(schema.profiles, bind=connection.engine) \
            .values(**values) \
            .on_conflict_do_update(index_elements=[schema.profiles.c.username], set_=updates)
        connection.execute(statement)

    def retrieve(self, username: str) -> Optional[Profile]:
        """Retrieve info about a single profile from the Internet.

        :param username: username of the profile to retrieve
        :return: profile metadata
        """

        try:
            profile = instaloader.Profile.from_username(self.instaloader_context, username)
            return Profile(
                username=profile.username,
                full_name=profile.full_name,
                biography=profile.biography,
            )
        except instaloader.ProfileNotExistsException:
            return None

    @staticmethod
    def exists(username: str, connection: sa.engine.Connection) -> bool:
        """Check if a profile exists.

        :param username: username of the profile to check
        :param connection: a database connection
        """

        statement = schema.profiles.select().where(schema.profiles.c.username == username)
        exists_statement = sa.select([sa.exists(statement)])
        return connection.execute(exists_statement).scalar()
