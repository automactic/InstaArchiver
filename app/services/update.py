import logging
from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.sql.operators
from typing import Optional
from . import schema
from .base import BaseService

logger = logging.getLogger(__name__)


class UpdateService(BaseService):
    EXPIRATION_THRESHOLD = timedelta(minutes=15)

    async def update_posts(self):
        """Update the posts of one profile."""

        async with self.database.transaction():
            if username := await self._find_next_profile():
                logger.debug(f'UpdateService: {username}')
                import asyncio
                await asyncio.sleep(20)
            else:
                logger.debug(f'No profile to update')

    async def _find_next_profile(self) -> Optional[str]:
        """Find username of the next profile to update.

        :return: username of the profile to update
        """

        statement = sa.select([schema.profiles.c.username], for_update=True) \
            .select_from(schema.profiles) \
            .where(sa.and_(
                sa.sql.operators.eq(schema.profiles.c.auto_update, True),
                sa.or_(
                    schema.profiles.c.last_update < datetime.utcnow() - self.EXPIRATION_THRESHOLD,
                    sa.sql.operators.eq(schema.profiles.c.last_update, None),
                )
            )) \
            .order_by(schema.profiles.c.last_update.desc().nullsfirst()) \
            .limit(1)
        result = await self.database.fetch_one(statement)
        return result.get('username')

    async def _find_latest_post_creation_time(self, username: str) -> Optional[datetime]:
        pass