import asyncio
import logging
import shutil
from datetime import timezone
from typing import Optional

import instaloader
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.profiles import Profile, PostsSummary, ProfileDetail, ProfileListResult, ProfileUpdates, ProfileWithStats
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

    async def list(self, search: Optional[str] = None, offset: int = 0, limit: int = 100) -> ProfileListResult:
        """List profiles.

        :param search: search text filter list of profiles
        :param offset: the number of profiles to skip
        :param limit: the number of profiles to fetch
        :return: the list query result
        """

        # fetch data
        base_query = schema.profiles.select()
        if search:
            conditions = [
                schema.profiles.c.username.ilike(f'%{search}%'),
                schema.profiles.c.full_name.ilike(f'%{search}%'),
                schema.profiles.c.display_name.ilike(f'%{search}%'),
            ]
            base_query = base_query.where(sa.or_(*conditions))
        base_query = base_query.cte('base_query')
        count_query = sa.select(sa.func.count().label('total_count')).select_from(base_query).cte('count_query')
        query = sa.select(
            base_query.c.username,
            base_query.c.full_name,
            base_query.c.display_name,
            base_query.c.biography,
            base_query.c.image_filename,
            count_query.c.total_count
        ).select_from(
            base_query.outerjoin(count_query, onclause=sa.sql.true(), full=True)
        ).order_by(base_query.c.display_name).offset(offset).limit(limit)
        rows = await self.database.fetch_all(query)

        # process result
        total_count = rows[0]['total_count']
        profiles = [Profile(**dict(row)) for row in rows] if total_count > 0 else []

        return ProfileListResult(profiles=profiles, limit=limit, offset=offset, count=total_count)

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

    async def get_statistics(self):
        """Get profile statistics."""

        # get data
        profiles = sa.select(
            schema.profiles.c.username,
            schema.profiles.c.full_name,
            schema.profiles.c.display_name,
            schema.profiles.c.biography,
            schema.profiles.c.image_filename,
            sa.func.min(schema.posts.c.timestamp).label('first_post_timestamp'),
            sa.func.max(schema.posts.c.timestamp).label('last_post_timestamp'),
            sa.func.count().label('total_count')
        ).select_from(
            schema.profiles.join(schema.posts, schema.profiles.c.username == schema.posts.c.username)
        ).group_by(schema.profiles.c.username).cte('profiles')
        quarters = sa.select(
            schema.posts.c.username,
            sa.func.cast(sa.func.date_part('year', schema.posts.c.timestamp), sa.INT).label('year'),
            sa.func.cast(sa.func.date_part('quarter', schema.posts.c.timestamp), sa.INT).label('quarter'),
            sa.func.count().label('count'),
        ).select_from(schema.posts).group_by(
            schema.posts.c.username, sa.literal_column('year'), sa.literal_column('quarter')
        ).cte('quarters')
        statement = sa.select(
            profiles.c.username,
            profiles.c.full_name,
            profiles.c.display_name,
            profiles.c.biography,
            profiles.c.image_filename,
            profiles.c.first_post_timestamp,
            profiles.c.last_post_timestamp,
            profiles.c.total_count,
            quarters.c.year,
            quarters.c.quarter,
            quarters.c.count,
        ).select_from(
            profiles.join(quarters, quarters.c.username == profiles.c.username)
        ).order_by(profiles.c.display_name)
        rows = await self.database.fetch_all(statement)

        # format result
        statistics = {}
        for row in rows:
            username = row['username']
            if username not in statistics:
                statistics[username] = ProfileWithStats(
                    username=row['username'],
                    full_name=row['full_name'],
                    display_name=row['display_name'],
                    biography=row['biography'],
                    image_filename=row['image_filename'],
                    first_post_timestamp=row['first_post_timestamp'].replace(tzinfo=timezone.utc),
                    last_post_timestamp=row['last_post_timestamp'].replace(tzinfo=timezone.utc),
                    total_count=row['total_count'],
                    counts={},
                )
            statistics[username].counts[f'{row["year"]}-Q{row["quarter"]}'] = row['count']

        return list(statistics.values())
