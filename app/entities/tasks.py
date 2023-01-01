from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from .enums import TaskType, TaskStatus


class Task(BaseModel):
    id: UUID
    username: str
    type: TaskType
    status: TaskStatus
    created: datetime
    started: Optional[datetime] = None
    completed: Optional[datetime] = None

    def __str__(self):
        return f'Task {self.type} | {self.username} | {self.status}'


class TaskCreateRequest(BaseModel):
    usernames: List[str]


class TaskListResponse(BaseModel):
    tasks: List[Task]
    limit: int
    offset: int
    count: int
