import logging
import mimetypes
import os
import pathlib
import shutil
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Optional

import aiohttp
import instaloader
import requests
from databases import Database

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, database: Database, http_session: aiohttp.ClientSession):
        self.database = database
        self.http_session = http_session

        # File IO Paths
        self.sessions_dir = Path('/sessions')
        self.media_dir = Path('/media')
        self.profile_images_dir = self.media_dir.joinpath('profile_images')
        self.post_dir = self.media_dir.joinpath('posts')
        self.thumb_images_dir = self.media_dir.joinpath('thumb_images')

        # Environment Variables
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME')
        try:
            self.user_id = int(os.getenv('USER_ID'))
        except ValueError:
            self.user_id = None
        try:
            self.group_id = int(os.getenv('GROUP_ID'))
        except ValueError:
            self.group_id = None

    @cached_property
    def instaloader(self):
        instance = instaloader.Instaloader()
        if username := self.instagram_username:
            path = str(self.sessions_dir.joinpath(f'{username}.session'))
            try:
                instance.load_session_from_file(username, path)
                logger.info(f'Loaded Instagram session for user {username}.')
            except FileNotFoundError:
                if password := os.getenv('INSTAGRAM_PASSWORD'):
                    try:
                        instance.login(username, password)
                        instance.save_session_to_file(path)
                        logger.info(f'Logged in to Instagram as user {username}.')
                    except instaloader.TwoFactorAuthRequiredException:
                        logger.error('Failed logging in to Instagram: two factor auth is not supported.')
                    except instaloader.InstaloaderException as e:
                        logger.error(f'Failed logging in to Instagram: {e}.')
                else:
                    logger.info(f'Unable to load Instagram session for user {username}.')
        return instance

    def _set_file_ownership(self, path: Path):
        """Change ownership of the directory or file to a specific user id or group id.

        :param path: the directory or file path to change the ownership
        """

        if self.user_id or self.group_id:
            shutil.chown(path, self.user_id, self.group_id)

    def _download(
        self, url: str, working_dir: Path, filename: str, timestamp: Optional[datetime] = None
    ) -> pathlib.Path:
        """Download a file from url to working dir with filename and optionally an access and update time.

        :param url: the url to retrieve the file
        :param working_dir: the dir to save the file
        :param filename: filename the file should be saved as (without extension)
        :param timestamp: access and update time of the file
        :return file_path: the path of the saved image or video
        """

        # retrieve file
        response = requests.get(url)

        # prepare working dir
        working_dir.mkdir(parents=True, exist_ok=True)
        self._set_file_ownership(working_dir)

        # prepare destination path
        extension = mimetypes.guess_extension(response.headers['content-type'])
        file_path = working_dir.joinpath(filename).with_suffix(extension)

        # save file data
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # set file access and update time
        if timestamp:
            os.utime(file_path, (timestamp.timestamp(), timestamp.timestamp()))

        # set file ownership
        self._set_file_ownership(file_path)

        return file_path

    def delete_file(self, working_dir: Path, *path_components):
        path = working_dir.joinpath(*path_components)
        self._set_file_ownership(path)
        path.unlink()
