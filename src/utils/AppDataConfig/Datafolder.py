# FlippyFlappingTheJ
# ./src/utils/AppDataConfig/Datafolder.py

import os

from src.utils.AppDataConfig.Config import ConfigurationFile


class DataFolder:

    def __init__(self):

        self._cwd = os.getcwd()
        self._assets_folder = os.path.join(rf"{self._cwd}", "assets")
        self._image_folder = os.path.join(self._assets_folder, "Images")
        self._temp_folder = os.path.join(self._assets_folder, "temp")
        self._config = ConfigurationFile(os.path.join(self._assets_folder, "config.json"))

    @property
    def assets_folder(self) -> str:
        return self._assets_folder

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def config(self) -> ConfigurationFile:
        return self._config

    @property
    def image_folder(self) -> str:
        return self._image_folder

    @property
    def temp_folder(self) -> str:
        return self._temp_folder
