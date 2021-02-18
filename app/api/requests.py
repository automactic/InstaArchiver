from pydantic import BaseModel


class PostCreationFromShortcode(BaseModel):
    shortcode: str
