from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from .tasks import BaseTask

class Profile(BaseModel):
    username: str
    display_name: str
    image_filename: str


class BaseStats(BaseModel):
    first_post_timestamp: Optional[datetime]
    last_post_timestamp: Optional[datetime]
    total_count: int
    counts: dict


class ProfileWithDetail(Profile):
    full_name: str
    biography: Optional[str] = None
    stats: BaseStats
    tasks: List[BaseTask] = []


class ProfileStats(BaseStats):
    username: str
    display_name: str


class ProfileListResult(BaseModel):
    data: List[Profile]
    limit: int
    offset: int
    count: int


class ProfileUpdates(BaseModel):
    display_name: Optional[str]