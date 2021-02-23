from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

import instaloader
from pydantic import BaseModel


class PostType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    SIDECAR = 'sidecar'

    @classmethod
    def from_instaloader(cls, type):
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
    index: int = 0
    url: Optional[str] = None
    filename: Optional[str] = None


@dataclass
class Post:
    shortcode: str
    owner_username: str
    creation_time: datetime
    type: PostType
    caption: Optional[str]
    items: List[PostItem]

    @classmethod
    def from_instaloader(cls, post: instaloader.Post):
        post_type = PostType.from_instaloader(post.typename)
        if post_type == PostType.IMAGE:
            items = [PostItem(type=PostItemType.IMAGE, url=post.url)]
        elif post_type == PostType.VIDEO:
            items = [PostItem(type=PostItemType.VIDEO, url=post.video_url)]
        elif post_type == PostType.SIDECAR:
            items = [
                PostItem(
                    type=PostItemType.VIDEO if node.is_video else PostItemType.IMAGE,
                    index=index,
                    url=node.video_url if node.is_video else node.display_url
                )
                for index, node in enumerate(post.get_sidecar_nodes())
            ]
        else:
            items = []

        return cls(
            shortcode=post.shortcode,
            owner_username=post.owner_username,
            creation_time=post.date_utc,
            type=post_type,
            caption=post.caption,
            items=items,
        )

    @property
    def response(self):
        return {
            'shortcode': self.shortcode,
            'owner_username': self.owner_username,
            'creation_time': self.creation_time.isoformat(),
        }


class Profile(BaseModel):
    username: str
    full_name: str
    biography: Optional[str] = None
    auto_update: bool = False
    last_update: Optional[datetime] = None


class ProfileListResult(BaseModel):
    profiles: List[Profile]
    limit: int
    offset: int
    count: int
