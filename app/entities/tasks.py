from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from .enums import TaskType, TaskStatus


class BaseTask(BaseModel):
    id: UUID
    type: TaskType
    status: TaskStatus
    created: datetime
    started: Optional[datetime] = None
    completed: Optional[datetime] = None
    post_count: Optional[int] = None
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None

class Task(BaseTask):
    username: Optional[str]
    user_display_name: Optional[str]

    def __str__(self):
        parts = [f'Task {self.type}', self.status]
        if self.username:
            parts.append(self.username)
        if self.status == TaskStatus.SUCCEEDED:
            parts.append(f'post count: {self.post_count}')
        return ' | '.join(parts)


class TaskCreateRequest(BaseModel):
    type: TaskType
    usernames: Optional[List[str]] = None
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None


class TaskListResponse(BaseModel):
    data: List[Task]
    limit: int
    offset: int
    count: int
