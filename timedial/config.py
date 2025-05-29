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

# ruff: noqa: D102
import logging
import os

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration model for the whole project."""

    _ephemeral: bool = not os.path.ismount("/home")
    guest_dir: str = "/data/guests"
    menu_file: str = "/opt/timedial/menu.yaml"
    ui_logger_path_str: str = "~/.timedial.log"
    ui_logger_level: int = logging.INFO
    auth_logger_level: int = logging.INFO

    @property
    def ui_logger_path(self) -> str:
        return os.path.expanduser(self.ui_logger_path_str)


config = Config()

if os.getenv("TIMEDIAL_ENV", "") == "local":
    config.guest_dir = "files/tmp"
    config.menu_file = "files/menu.yaml"
    ui_logger_path_str = "files/log/timedial.log"
    ui_logger_level: int = logging.DEBUG
    auth_logger_level: int = logging.DEBUG
