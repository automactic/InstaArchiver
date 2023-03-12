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
        base_cte = schema.tasks.select().where(*condition).cte('base')

        # build count query
        count_cte = sa.select(sa.func.count().label('total_count')).select_from(base_cte).cte('count')

        # build final query
        order_by_clause = base_cte.c.created.asc() if is_ascending else base_cte.c.created.desc()
        query = sa.select(
            base_cte.c.id,
            base_cte.c.username,
            schema.profiles.c.display_name.label('user_display_name'),
            base_cte.c.type,
            base_cte.c.status,
            base_cte.c.created,
            base_cte.c.started,
            base_cte.c.completed,
            base_cte.c.post_count,
            base_cte.c.time_range_start,
            base_cte.c.time_range_end,
            count_cte.c.total_count,
        ).select_from(
            base_cte.outerjoin(
                schema.profiles, base_cte.c.username == schema.profiles.c.username, full=False
            ).outerjoin(count_cte, sa.sql.true(), full=True)
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

    async def set_in_progress(self, task):
        """Set task status to in_progress.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.IN_PROGRESS
        task.started = datetime.utcnow()

        updates = {'status': task.status, 'started': task.started}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

    async def set_succeeded(self, task):
        """Set task status to succeeded.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.SUCCEEDED
        task.completed = datetime.utcnow()

        updates = {'status': task.status, 'completed': task.completed, 'post_count': task.post_count}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

    async def set_failed(self, task):
        """Set task status to failed.

        :param task: the task to update
        :return: the updated task
        """

        task.status = TaskStatus.FAILED
        task.completed = datetime.utcnow()

        updates = {'status': task.status, 'completed': task.completed, 'post_count': task.post_count}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)

    async def set_post_count(self, task):
        """Set task post count value.

        :param task: the task to update
        """

        updates = {'post_count': task.post_count}
        statement = sa.update(schema.tasks).where(schema.tasks.c.id == task.id).values(**updates)
        await self.database.execute(statement)


class TaskExecutor(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_crud_service = TaskCRUDService(*args, **kwargs)
        self.post_crud_service = PostService(*args, **kwargs)

    async def run_tasks(self):
        """Run all tasks one after another."""

        while task := await self.task_crud_service.get_next():
            await self.task_crud_service.set_in_progress(task)
            logger.debug(f'Executing task: {task}')

            try:
                if task.type == TaskType.CATCH_UP:
                    await self._run_catch_up_task(task)
                elif task.type == TaskType.SAVED_POSTS:
                    await self._run_saved_posts_task(task)
                elif task.type == TaskType.TIME_RANGE:
                    await self._run_time_range_task(task)
                else:
                    raise NotImplemented('Unrecognized task type')
                await self.task_crud_service.set_succeeded(task)
                logger.info(f'Task succeeded: {task}')
            except Exception as e:
                await self.task_crud_service.set_failed(task)
                logger.error(f'Task failed: {task}, {e}', exc_info=True)

    async def _sleep(self):
        """Sleep for a random amount of time."""

        max_sleep = os.environ.get('MAX_SLEEP', 60)
        await asyncio.sleep(random.randint(0, max_sleep))

    async def _get_profile(self, username) -> instaloader.Profile:
        """Get instaloader profile for a user.

        :param username: name of the user whose profile to get
        :return: the instaloader profile
        """

        loop = asyncio.get_running_loop()
        try:
            func = instaloader.Profile.from_username
            return await loop.run_in_executor(None, func, self.instaloader.context, username)
        except instaloader.ProfileNotExistsException:
            logger.debug(f'Profile {username} does not exist.')
            raise

    async def _run_catch_up_task(self, task: Task):
        """Run catch-up task.

        :param task: the task to run
        """

        loop = asyncio.get_running_loop()
        profile = await self._get_profile(task.username)
        post_iterator = await loop.run_in_executor(None, profile.get_posts)
        task.post_count = 0

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
            task.post_count += 1

            # update post count
            await self.task_crud_service.set_post_count(task)

    async def _run_saved_posts_task(self, task: Task):
        """Run saved posts task.

        :param task: the task to run
        """

        loop = asyncio.get_running_loop()
        profile = await self._get_profile(self.instagram_username)
        post_iterator = await loop.run_in_executor(None, profile.get_saved_posts)
        task.post_count = 0

        while True:
            # sleep for a random amount of time
            await self._sleep()

            # fetch the next post
            try:
                post: instaloader.Post = await loop.run_in_executor(None, next, post_iterator)
            except StopIteration:
                logger.debug('Unable to get the next post.')
                break

            # complete task if a post already exists
            if await self.post_crud_service.exists(post.shortcode):
                break

            # save post
            await self.post_crud_service.create_from_instaloader(post)
            task.post_count += 1

            # update post count
            await self.task_crud_service.set_post_count(task)

    async def _run_time_range_task(self, task: Task):
        """Run time range task.
        
        :param task: the task to run
        """

        loop = asyncio.get_running_loop()
        profile = await self._get_profile(task.username)
        post_iterator = await loop.run_in_executor(None, profile.get_posts)
        task.post_count = 0

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

            # if post is later than the end date, that means we have yet to reach posts within the time range
            if post.date_utc >= task.time_range_end:
                logger.debug(f'Post date {post.date_utc} is later than the end date.')
                continue

            # if post is earlier than the start date, that means we have iterated through posts within the time range
            if post.date_utc < task.time_range_start:
                logger.debug(f'Post date {post.date_utc} is earlier than the start date.')
                break

            # save post
            await self.post_crud_service.create_from_instaloader(post)
            task.post_count += 1

            # update post count
            await self.task_crud_service.set_post_count(task)
