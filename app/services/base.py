import mimetypes
import os
import shutil
from pathlib import Path

import aiofiles
import aiohttp
import instaloader
import yarl
from databases import Database
from datetime import datetime
from typing import Optional
class BaseService:
    def __init__(self, database: Database, http_session: aiohttp.ClientSession):
        self.database = database
        self.http_session = http_session
        self.instaloader_context = instaloader.InstaloaderContext()

        self.media_dir = Path('/media')
        self.post_dir = self.media_dir.joinpath('posts')
        self.thumb_images_dir = self.media_dir.joinpath('thumb_images')
        self.recycle_dir = self.media_dir.joinpath('recycle')
        try:
            self.user_id = int(os.getenv('USER_ID'))
        except ValueError:
            self.user_id = None
        try:
            self.group_id = int(os.getenv('GROUP_ID'))
        except ValueError:
            self.group_id = None

    def _set_file_ownership(self, path: Path):
        """Change ownership of the directory or file to a specific user id or group id.

        :param path: the directory or file path to change the ownership
        """

        if self.user_id or self.group_id:
            shutil.chown(path, self.user_id, self.group_id)

    async def save_media(self, url: str, destination: Path, file_name: str) -> Path:
        """Save a image or video to a destination with a file name.

        :param url: the url to retrieve the image or video
        :param destination: the destination dir to save the file, relative to the media dir
        :param file_name: file name, without extension
        :return file_path: the path of the saved image or video
        """

        async with self.http_session.get(yarl.URL(url, encoded=True)) as response:
            # setup the working dir
            dir_path = self.media_dir.joinpath(destination)
            dir_path.mkdir(parents=True, exist_ok=True)
            self._set_file_ownership(dir_path)

            # save the file
            extension = mimetypes.guess_extension(response.content_type)
            file_path = dir_path.joinpath(file_name).with_suffix(extension)
            async with aiofiles.open(file_path, 'wb') as file:
                data = await response.read()
                await file.write(data)
                self._set_file_ownership(file_path)

            return file_path

    async def _download(self, url: str, working_dir: Path, filename: str, timestamp: Optional[datetime] = None):
        """Download a file from url to working dir with filename and optionally an access and update time.

        :param url: the url to retrieve the file
        :param working_dir: the dir to save the file
        :param filename: filename the file should be saved as (without extension)
        :param timestamp: access and update time of the file
        :return file_path: the path of the saved image or video
        """

        async with self.http_session.get(yarl.URL(url, encoded=True)) as response:
            # prepare working dir
            working_dir.mkdir(parents=True, exist_ok=True)
            self._set_file_ownership(working_dir)

            # prepare destination path
            extension = mimetypes.guess_extension(response.content_type)
            file_path = working_dir.joinpath(filename).with_suffix(extension)

            # save the file
            async with aiofiles.open(file_path, 'wb') as file:
                data = await response.read()
                await file.write(data)

            # set file access and update time
            if timestamp:
                os.utime(file_path, (timestamp.timestamp(), timestamp.timestamp()))

            # set file ownership
            self._set_file_ownership(file_path)
