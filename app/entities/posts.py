from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'


class Post(BaseModel):
    shortcode: str
    owner_username: str
    creation_time: datetime
    type: PostType
    caption: Optional[str]
    caption_hashtags: [str]
    caption_mentions: [str]


class PostListResult(BaseModel):
    posts: List[Post]
    limit: int
    offset: int
    count: int


class PostCreationFromShortcode(BaseModel):
    shortcode: str


class PostCreationFromTimeRange(BaseModel):
    username: str
    start: datetime
    end: datetime
