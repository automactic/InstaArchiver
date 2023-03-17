import asyncio
from collections import defaultdict
from datetime import timezone
from typing import Dict, Optional

import sqlalchemy as sa

from entities.profiles import (
    Profile,
    BaseStats,
    ProfileWithDetail,
    ProfileStats,
    ProfileListResult,
)
from entities.tasks import BaseTask
from services import schema
from services.base import BaseService
from .task import TaskCRUDService


class ProfileCRUDService(BaseService):
    async def list(
        self, search: Optional[str] = None, offset: int = 0, limit: int = 100
    ) -> ProfileListResult:
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
                schema.profiles.c.username.ilike(f"%{search}%"),
                schema.profiles.c.full_name.ilike(f"%{search}%"),
                schema.profiles.c.display_name.ilike(f"%{search}%"),
            ]
            base_query = base_query.where(sa.or_(*conditions))
        base_query = base_query.cte("base_query")
        count_query = (
            sa.select(sa.func.count().label("total_count"))
            .select_from(base_query)
            .cte("count_query")
        )
        query = (
            sa.select(
                base_query.c.username,
                base_query.c.full_name,
                base_query.c.display_name,
                base_query.c.biography,
                base_query.c.image_filename,
                count_query.c.total_count,
            )
            .select_from(
                base_query.outerjoin(count_query, onclause=sa.sql.true(), full=True)
            )
            .order_by(base_query.c.display_name)
            .offset(offset)
            .limit(limit)
        )
        rows = await self.database.fetch_all(query)

        # process result
        total_count = rows[0]["total_count"]
        profiles = [Profile(**dict(row)) for row in rows] if total_count > 0 else []

        return ProfileListResult(
            profiles=profiles, limit=limit, offset=offset, count=total_count
        )

    async def get(self, username: str) -> Optional[ProfileWithDetail]:
        """Get a single profile with post stats and recent tasks."""

        query = (
            sa.select(
                schema.profiles.c.username,
                schema.profiles.c.full_name,
                schema.profiles.c.display_name,
                schema.profiles.c.biography,
                schema.profiles.c.image_filename,
            )
            .select_from(schema.profiles)
            .where(schema.profiles.c.username == username)
        )
        profile_info, stats, tasks = await asyncio.gather(
            self.database.fetch_one(query),
            self.get_stats(username),
            TaskCRUDService(self.database, self.http_session).list(
                limit=5, username=username, is_ascending=False
            ),
        )

        profile = ProfileWithDetail(
            **dict(profile_info),
            stats=BaseStats(**stats[username].dict()),
            tasks=[BaseTask(**task.dict()) for task in tasks.tasks],
        )
        return profile

    async def get_stats(
        self, username: Optional[str] = None
    ) -> Dict[str, ProfileStats]:
        """Get post stats."""

        # build conditions
        conditions = []
        if username:
            conditions.append(schema.profiles.c.username == username)

        # build profiles and quarters cte
        profiles_cte = (
            sa.select(
                schema.profiles.c.username,
                schema.profiles.c.display_name,
                sa.func.min(schema.posts.c.timestamp).label("first_post_timestamp"),
                sa.func.max(schema.posts.c.timestamp).label("last_post_timestamp"),
                sa.func.count().label("total_count"),
            )
            .select_from(
                schema.profiles.join(
                    schema.posts, schema.profiles.c.username == schema.posts.c.username
                )
            )
            .where(*conditions)
            .group_by(schema.profiles.c.username)
            .cte("profiles")
        )
        quarters_cte = (
            sa.select(
                schema.posts.c.username,
                sa.func.cast(
                    sa.func.date_part("year", schema.posts.c.timestamp), sa.INT
                ).label("year"),
                sa.func.cast(
                    sa.func.date_part("quarter", schema.posts.c.timestamp), sa.INT
                ).label("quarter"),
                sa.func.count().label("count"),
            )
            .select_from(schema.posts)
            .group_by(
                schema.posts.c.username,
                sa.literal_column("year"),
                sa.literal_column("quarter"),
            )
            .cte("quarters")
        )

        # build query and get data
        statement = (
            sa.select(
                profiles_cte.c.username,
                profiles_cte.c.display_name,
                profiles_cte.c.first_post_timestamp,
                profiles_cte.c.last_post_timestamp,
                profiles_cte.c.total_count,
                quarters_cte.c.year,
                quarters_cte.c.quarter,
                quarters_cte.c.count,
            )
            .select_from(
                profiles_cte.join(
                    quarters_cte, quarters_cte.c.username == profiles_cte.c.username
                )
            )
            .order_by(
                profiles_cte.c.display_name, quarters_cte.c.year, quarters_cte.c.quarter
            )
        )
        rows = await self.database.fetch_all(statement)

        # format result
        profile_stats = {}
        for row in rows:
            username = row["username"]
            stats = profile_stats.get(
                username,
                ProfileStats(
                    username=username,
                    display_name=row["display_name"],
                    first_post_timestamp=row["first_post_timestamp"].replace(
                        tzinfo=timezone.utc
                    ),
                    last_post_timestamp=row["last_post_timestamp"].replace(
                        tzinfo=timezone.utc
                    ),
                    total_count=row["total_count"],
                    counts=defaultdict(dict),
                ),
            )
            stats.counts[str(row["year"])][f"Q{row['quarter']}"] = row["count"]
            profile_stats[username] = stats
        return profile_stats
