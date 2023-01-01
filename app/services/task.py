import asyncio
import logging
import os
import random
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import instaloader
import pydantic
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from entities.enums import TaskType, TaskStatus
from entities.tasks import Task, TaskCreateRequest, TaskListResponse
from services import schema
from services.post import PostService
from .base import BaseService

logger = logging.getLogger(__name__)


class TaskCRUDService(BaseService):
    async def create(self, request: TaskCreateRequest) -> [Task]:
        """Create tasks.

        :param request: request to create tasks
        :return: tasks that are created
        """

        tasks = [
            Task(
                id=uuid4(),
                username=username,
                type=TaskType.CATCH_UP,
                status=TaskStatus.PENDING,
                created=datetime.utcnow(),
            )
            for username in request.usernames
        ]
        values = [task.dict(exclude_unset=True) for task in tasks]
        statement = insert(schema.tasks).values(values).on_conflict_do_nothing()
        await self.database.execute(statement)
        return tasks

    async def list(
        self, offset: int = 0, limit: int = 10, status: List[TaskStatus] = None, is_ascending: bool = True
    ):
        """List tasks.

        :param offset: the number of tasks to skip
        :param limit: the number of tasks to fetch
        :param status: task status to filter
        :param is_ascending: if task created earlier should appear in the list first
        :return: list task result
        """

        # build base query
        condition = []
        if status:
            condition.append(schema.tasks.c.status.in_(status))
        base_query = schema.tasks.select().where(sa.and_(*condition)).cte('base_query')

        # build count query
        count_query = sa.select(sa.func.count().label('total_count')).select_from(base_query).cte('count_query')

        # build final query
        order_by_clause = base_query.c.created.asc() if is_ascending else base_query.c.created.desc()
        query = sa.select(
            base_query.c.id.label('id'),
            base_query.c.username.label('username'),
            base_query.c.type.label('type'),
            base_query.c.status.label('status'),
            base_query.c.created.label('created'),
            base_query.c.started.label('started'),
            base_query.c.completed.label('completed'),
            count_query.c.total_count.label('total_count'),
        ).select_from(
            base_query.outerjoin(count_query, sa.sql.true(), full=True)
        ).order_by(order_by_clause).offset(offset).limit(limit)

        # format result
        tasks, count = [], 0
        for result in await self.database.fetch_all(query):
            count = result['total_count']
            try:
                task = Task(**dict(result))
                tasks.append(task)
            except pydantic.error_wrappers.ValidationError:
                continue

        return TaskListResponse(tasks=tasks, limit=limit, offset=offset, count=count)

    async def get_next(self) -> Optional[Task]:
        """Get the next task to execute.

        :return: next task to execute
        """

        result = await self.list(offset=0, limit=1, status=[TaskStatus.PENDING], is_ascending=True)
        return result.tasks[0] if result.tasks else None

    async def set_in_progress(self, task) -> Task:
        """Set task status to in_progress.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.IN_PROGRESS
        task.started = datetime.utcnow()

        updates = {'status': task.status, 'started': task.started}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

        return task

    async def set_succeeded(self, task) -> Task:
        """Set task status to succeeded.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.SUCCEEDED
        task.completed = datetime.utcnow()

        updates = {'status': task.status, 'completed': task.completed}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

        return task

    async def set_failed(self, task) -> Task:
        """Set task status to failed.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.FAILED
        task.completed = datetime.utcnow()

        updates = {'status': task.status, 'completed': task.completed}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

        return task


class TaskExecutor(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_crud_service = TaskCRUDService(*args, **kwargs)
        self.post_crud_service = PostService(*args, **kwargs)

    async def run_tasks(self):
        """Run all tasks one after another."""

        while task := await self.task_crud_service.get_next():
            task = await self.task_crud_service.set_in_progress(task)
            logger.debug(f'Executing task: {task}')

            try:
                if task.type == TaskType.CATCH_UP:
                    await self._run_catch_up_task(task)
                task = await self.task_crud_service.set_succeeded(task)
                logger.info(f'Task succeeded: {task}')
            except:
                task = await self.task_crud_service.set_failed(task)
                logger.error(f'Task failed: {task}')

    async def _sleep(self):
        """Sleep for a random amount of time."""

        max_sleep = os.environ.get('MAX_SLEEP', 60)
        await asyncio.sleep(random.randint(0, max_sleep))

    async def _get_post_iterator(self, username) -> instaloader.NodeIterator:
        """Get the post iterator for a user.

        :param username: name of the user whose posts to iterate
        :return: the post iterator
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            profile = await loop.run_in_executor(None, func, self.instaloader.context, username)
            return await loop.run_in_executor(None, profile.get_posts)
        except instaloader.ProfileNotExistsException:
            logger.debug(f'Failed to get post iterator. Profile {username} does not exist.')
            raise

    async def _run_catch_up_task(self, task):
        """Run catch-up task.

        :param task: the task to run
        """

        loop = asyncio.get_running_loop()
        post_iterator = await self._get_post_iterator(task.username)

        while True:
            # sleep for a random amount of time
            await self._sleep()

            # fetch the next post
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
            except StopIteration:
                logger.debug('Unable to get the next post.')
                break

            # skip pinned posts
            if post.is_pinned:
                continue

            # complete task if a post already exists
            if await self.post_crud_service.exists(post.shortcode):
                break

            # save post
            await self.post_crud_service.create_from_instaloader(post)
