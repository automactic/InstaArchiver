from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import pydantic
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.enums import TaskType, TaskStatus
from entities.tasks import Task, TaskCreateRequest, TaskListResponse
from services import schema
from ..base import BaseService


class TaskCRUDService(BaseService):
    async def create(self, request: TaskCreateRequest) -> [Task]:
        """Create tasks.

        :param request: request for task creation
        :return: tasks that are created
        """

        if request.type in [TaskType.CATCH_UP, TaskType.TIME_RANGE]:
            tasks = [
                Task(
                    id=uuid4(),
                    username=username,
                    type=request.type,
                    status=TaskStatus.PENDING,
                    created=datetime.utcnow(),
                    time_range_start=request.time_range_start,
                    time_range_end=request.time_range_end,
                )
                for username in request.usernames
            ]
        elif request.type == TaskType.SAVED_POSTS:
            tasks = [
                Task(
                    id=uuid4(),
                    username=None,
                    type=TaskType.SAVED_POSTS,
                    status=TaskStatus.PENDING,
                    created=datetime.utcnow(),
                )
            ]
        else:
            tasks = []
        values = [task.dict(exclude_unset=True) for task in tasks]
        statement = insert(schema.tasks).values(values).on_conflict_do_nothing()
        await self.database.execute(statement)
        return tasks

    async def list(
        self,
        offset: int = 0,
        limit: int = 10,
        status: List[TaskStatus] = None,
        username: Optional[str] = None,
        is_ascending: bool = True,
    ):
        """List tasks.

        :param offset: the number of tasks to skip
        :param limit: the number of tasks to fetch
        :param status: task status to filter
        :param username: task username to filter
        :param is_ascending: if task created earlier should appear in the list first
        :return: list task result
        """

        # build base query
        condition = []
        if status:
            condition.append(schema.tasks.c.status.in_(status))
        if username:
            condition.append(schema.tasks.c.username == username)
        base_cte = schema.tasks.select().where(*condition).cte("base")

        # build count query
        count_cte = (
            sa.select(sa.func.count().label("total_count"))
            .select_from(base_cte)
            .cte("count")
        )

        # build final query
        order_by_clause = (
            base_cte.c.created.asc() if is_ascending else base_cte.c.created.desc()
        )
        query = (
            sa.select(
                base_cte.c.id,
                base_cte.c.username,
                schema.profiles.c.display_name.label("user_display_name"),
                base_cte.c.type,
                base_cte.c.status,
                base_cte.c.created,
                base_cte.c.started,
                base_cte.c.completed,
                base_cte.c.post_count,
                base_cte.c.time_range_start,
                base_cte.c.time_range_end,
                count_cte.c.total_count,
            )
            .select_from(
                base_cte.outerjoin(
                    schema.profiles,
                    base_cte.c.username == schema.profiles.c.username,
                    full=False,
                ).outerjoin(count_cte, sa.sql.true(), full=True)
            )
            .order_by(order_by_clause)
            .offset(offset)
            .limit(limit)
        )

        # format result
        tasks, count = [], 0
        for result in await self.database.fetch_all(query):
            count = result["total_count"]
            try:
                task = Task(**dict(result))
                tasks.append(task)
            except pydantic.error_wrappers.ValidationError:
                continue

        return TaskListResponse(data=tasks, limit=limit, offset=offset, count=count)

    async def get_next(self) -> Optional[Task]:
        """Get the next task to execute.

        :return: next task to execute
        """

        tasks = await self.list(
            offset=0, limit=1, status=[TaskStatus.PENDING], is_ascending=True
        )
        return tasks.data[0] if tasks.data else None

    async def set_in_progress(self, task):
        """Set task status to in_progress.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.IN_PROGRESS
        task.started = datetime.utcnow()

        updates = {"status": task.status, "started": task.started}
        statement = (
            sa.update(schema.tasks)
            .where(schema.tasks.c.id == task.id)
            .values(**updates)
        )
        await self.database.execute(statement)

    async def set_succeeded(self, task):
        """Set task status to succeeded.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.SUCCEEDED
        task.completed = datetime.utcnow()

        updates = {
            "status": task.status,
            "completed": task.completed,
            "post_count": task.post_count,
        }
        statement = (
            sa.update(schema.tasks)
            .where(schema.tasks.c.id == task.id)
            .values(**updates)
        )
        await self.database.execute(statement)

    async def set_failed(self, task):
        """Set task status to failed.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.FAILED
        task.completed = datetime.utcnow()

        updates = {
            "status": task.status,
            "completed": task.completed,
            "post_count": task.post_count,
        }
        statement = (
            sa.update(schema.tasks)
            .where(schema.tasks.c.id == task.id)
            .values(**updates)
        )
        await self.database.execute(statement)

    async def set_post_count(self, task):
        """Set task post count value.

        :param task: the task to update
        """

        updates = {"post_count": task.post_count}
        statement = (
            sa.update(schema.tasks)
            .where(schema.tasks.c.id == task.id)
            .values(**updates)
        )
        await self.database.execute(statement)
