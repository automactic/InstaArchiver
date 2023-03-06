from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class Profile(BaseModel):
    username: str
    full_name: str
    display_name: str
    biography: Optional[str] = None
    image_filename: str


class PostsSummary(BaseModel):
    count: int
    earliest_timestamp: Optional[datetime]
    latest_timestamp: Optional[datetime]


class ProfileDetail(Profile):
    posts: PostsSummary


class ProfileListResult(BaseModel):
    profiles: List[Profile]
    limit: int
    offset: int
    count: int


class ProfileUpdates(BaseModel):
    display_name: Optional[str]


class ProfileWithStats(BaseModel):
    username: str
    full_name: str
    display_name: str
    biography: Optional[str] = None
    image_filename: str
    first_post_timestamp: Optional[datetime]
    last_post_timestamp: Optional[datetime]
    total_count: int
    counts: dict
