from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'

    @classmethod
    def from_instagram(cls, type):
        if type == 'GraphImage':
            return cls.IMAGE
        elif type == 'GraphVideo':
            return cls.VIDEO
        elif type == 'GraphSidecar':
            return cls.SIDECAR
        else:
            return None


class PostItemType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'


@dataclass
class PostItem:
    type: PostItemType
    url: str
    index: int = 0


@dataclass
class Post:
    shortcode: str
    owner_username: str
    creation_time: datetime
    type: PostType
    caption: Optional[str]
    items: List[PostItem]


@dataclass
class Profile:
    username: str
    full_name: str
    biography: Optional[str] = None
    auto_update: bool = False
    last_update: Optional[datetime] = None
