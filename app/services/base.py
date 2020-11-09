import os
import shutil
from pathlib import Path

import instaloader


class BaseService:
    def __init__(self):
        self.instaloader_context = instaloader.InstaloaderContext()
        self.data_dir = Path('/data')

        try:
            self.user_id = int(os.getenv('USER_ID'))
        except ValueError:
            self.user_id = None
        try:
            self.group_id = int(os.getenv('GROUP_ID'))
        except ValueError:
            self.group_id = None

    def _change_file_ownership(self, path):
        """Change ownership of the directory or file to a specific user id or group id.

        :param path: the directory or file path to change the ownership
        """

        if self.user_id or self.group_id:
            shutil.chown(path, self.user_id, self.group_id)
