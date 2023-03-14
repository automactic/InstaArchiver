import asyncio
import logging
import shutil

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.profiles import ProfileUpdates
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
            profile = await loop.run_in_executor(None, func, self.instaloader.context, username)
        except instaloader.ProfileNotExistsException:
            logger.warning(f'Profile does not exist: {username}')
            return

        # save profile image
        image_path = self._download(profile.profile_pic_url, self.profile_images_dir, profile.username)

        # upsert profile
        values = {
            'username': profile.username,
            'full_name': profile.full_name,
            'display_name': profile.full_name,
            'biography': profile.biography,
            'image_filename': image_path.parts[-1],
            'auto_archive': False,
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

        statement = sa.select(schema.profiles.c.username).where(schema.profiles.c.username == username)
        exists_statement = sa.select(sa.exists(statement))
        return await self.database.fetch_val(query=exists_statement)

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

    async def delete(self, username: str):
        """Delete a profile.

        :param username: username of the profile to delete
        """

        # delete files
        try:
            self.delete_file(self.profile_images_dir, f'{username}.jpg')
            shutil.rmtree(self.thumb_images_dir.joinpath(username))
            shutil.rmtree(self.post_dir.joinpath(username))
        except FileNotFoundError:
            pass

        # delete records in database
        schema.profiles.delete()
        statement = sa.delete(schema.profiles) \
            .where(schema.profiles.c.username == username) \
            .returning(schema.profiles.c.username)
        await self.database.execute(statement)
