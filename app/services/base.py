import mimetypes
from pathlib import Path

import aiohttp
import yarl
from databases import Database


class BaseService:
    def __init__(self, database: Database, http_session: aiohttp.ClientSession):
        self.database = database
        self.http_session = http_session
        self.media_dir = Path('/media')

    async def save_media(self, url: str, destination: Path, file_name: str):
        async with self.http_session.get(yarl.URL(url, encoded=True)) as response:
            # get extension
            extension = mimetypes.guess_extension(response.content_type)
            print(('extension', extension))
            if not extension:
                return

