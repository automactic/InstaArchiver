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
    SAVED_POSTS = 'saved_posts'
    TIME_RANGE = 'time_range'


class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
