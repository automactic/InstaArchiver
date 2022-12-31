from enum import Enum


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'


class PostItemType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'


class TaskType(str, Enum):
    CATCH_UP = 'catch_up'


class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ERROR = 'error'
