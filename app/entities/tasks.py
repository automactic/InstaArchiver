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


class TaskListResponse(BaseModel):
    tasks: List[Task]
    limit: int
    offset: int
    count: int


class TaskCreateRequest(BaseModel):
    usernames: List[str]
