# FlippyFlappingTheJ
# ./src/FFTJ.py

import atexit
import os

from src.UI.FFTJScreen import FFTJUI
from src.utils.AppDataConfig.Datafolder import DataFolder


class FFTJAppManager:

    def __init__(self, v: str):

        self.VERSION = v
        self._status: int = -1
        self.DATAFOLDER: DataFolder = DataFolder()

        atexit.register(self._clean_temp_folder)  # Clean temp folder when program exits

        self.CLIENT: FFTJUI = FFTJUI(self)

    def _clean_temp_folder(self):
        files = os.listdir(self.datafolder.temp_folder)
        for file in files:
            fp = os.path.join(self.datafolder.temp_folder, file)
            os.remove(fp)

    @property
    def version(self) -> str:
        return self.VERSION

    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, state: int):
        self._status = state

    @property
    def datafolder(self) -> DataFolder:
        return self.DATAFOLDER
