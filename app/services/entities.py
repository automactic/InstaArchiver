from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import instaloader

from entities.posts import PostType, PostItemType


@dataclass
class PostItem:
    type: PostItemType
    index: int = 0
    duration: Optional[float] = None
    filename: Optional[str] = None
    thumb_image_filename: Optional[str] = None
    url: Optional[str] = None
    thumb_url: Optional[str] = None


@dataclass
class Post:
    shortcode: str
    username: str
    timestamp: datetime
    type: PostType
    caption: Optional[str]
    caption_hashtags: [str]
    caption_mentions: [str]
    items: List[PostItem]

    @classmethod
    def from_instaloader(cls, post: instaloader.Post):
        if post.typename == 'GraphImage':
            post_type = PostType.IMAGE
            items = [PostItem(type=PostItemType.IMAGE, url=post.url)]
        elif post.typename == 'GraphVideo':
            post_type = PostType.VIDEO
            items = [
                PostItem(type=PostItemType.VIDEO, url=post.video_url, thumb_url=post.url, duration=post.video_duration)
            ]
        elif post.typename == 'GraphSidecar':
            post_type = PostType.SIDECAR
            items = [
                PostItem(
                    type=PostItemType.VIDEO if node.is_video else PostItemType.IMAGE,
                    index=index,
                    url=node.video_url if node.is_video else node.display_url,
                    thumb_url=node.display_url if node.is_video else None,
                )
                for index, node in enumerate(post.get_sidecar_nodes())
            ]
        else:
            post_type = None
            items = []

        return cls(
            shortcode=post.shortcode,
            username=post.owner_username,
            timestamp=post.date_utc,
            type=post_type,
            caption=post.caption,
            caption_hashtags=post.caption_hashtags,
            caption_mentions=post.caption_mentions,
            items=items,
        )

    @property
    def response(self):
        return {
            'shortcode': self.shortcode,
            'username': self.username,
            'timestamp': self.timestamp.isoformat(),
        }
