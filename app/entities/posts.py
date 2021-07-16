from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'


class PostItemType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'


class PostItem(BaseModel):
    index: int
    type: PostItemType
    duration: Optional[float] = None
    filename: Optional[str] = None
    thumb_image_filename: Optional[str] = None


class Post(BaseModel):
    shortcode: str
    username: str
    timestamp: datetime
    type: PostType
    caption: Optional[str]
    caption_hashtags: List[str]
    caption_mentions: List[str]
    items: List[PostItem]


class PostListResult(BaseModel):
    posts: List[Post]
    limit: int
    offset: int
    count: int


class PostCreationFromShortcode(BaseModel):
    shortcode: str


class PostArchiveRequest:
    class FromTimeRange(BaseModel):
        username: str  # username of the profile to archive posts
        start: datetime  # start of the time range to archive posts
        end: datetime  # end of the time range to archive posts
        saved_only: Optional[bool] = False  # if True, only posts that are marked saved by the user will be archived
