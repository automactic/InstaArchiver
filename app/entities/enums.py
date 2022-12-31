from enum import Enum


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'


class PostItemType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'


class TaskType(Enum):
    CATCH_UP = 'catch_up'
