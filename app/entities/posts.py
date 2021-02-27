from datetime import datetime

from pydantic import BaseModel


class PostCreationFromShortcode(BaseModel):
    shortcode: str


class PostCreationFromTimeRange(BaseModel):
    username: str
    start: datetime
    end: datetime
