"""TimeDial project.

Copyright (c) Martin Miedema
Repository: https://github.com/number42net/timedial

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import os

from pydantic import BaseModel


class Config(BaseModel):
    """Base configuration model for the TimeDial project."""

    _ephemeral: bool = not os.path.ismount("/home")
    guest_dir: str = "/data/guests"
    menu_file: str = "/opt/timedial/menu.yaml"
    simulator_path: str = "/opt/simulators"
    ui_logger_path_str: str = "~/.timedial.log"
    ui_logger_level: int = logging.INFO
    auth_logger_level: int = logging.INFO
    stale_files_size: int = 20 * 1024 * 1024  # 20MiB
    stale_files_age: int = 24 * 3600  # 24 hours
    stale_files_sleep: int = 60 * 60  # Once per hour

    @property
    def ui_logger_path(self) -> str:
        """Returns the expanded file system path for the UI log file.

        Returns:
            str: Absolute path with '~' expanded to the user's home directory.
        """
        return os.path.expanduser(self.ui_logger_path_str)


config = Config()

if os.getenv("TIMEDIAL_ENV", "") == "local":
    config.guest_dir = "files/data/guests"
    config.menu_file = "files/opt/timedial/menu.yaml"
    # config.ui_logger_path_str = "files/log/timedial.log"
    config.ui_logger_level = logging.DEBUG
    config.auth_logger_level = logging.DEBUG
    config.simulator_path = "files/opt/simulators"
