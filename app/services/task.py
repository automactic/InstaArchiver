import asyncio
import logging
import os
import random

import instaloader

from entities.enums import TaskType
from entities.tasks import Task
from services.post import PostService
from .base import BaseService
from .crud import TaskCRUDService

logger = logging.getLogger(__name__)


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
