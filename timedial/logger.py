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
import logging.handlers
import os

from timedial.config import config


def ui_logger_config() -> None:
    """Configures the UI logger.

    Sets the log level, disables propagation, and adds a file handler
    with timestamped formatting for UI-related logs.
    """
    ui_logger = logging.getLogger("timedial")
    ui_logger.handlers.clear()
    ui_logger.setLevel(config.ui_logger_level)
    ui_logger.propagate = False

    file_handler = logging.FileHandler(config.ui_logger_path)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s: %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    ui_logger.addHandler(file_handler)


def auth_logger_config() -> None:
    """Configures the authentication logger.

    Sets the log level, disables propagation, and adds a syslog handler
    using the appropriate system socket. This is intended for security-related logs.
    """
    auth_logger = logging.getLogger("timedial")
    auth_logger.handlers.clear()
    auth_logger.setLevel(config.auth_logger_level)
    auth_logger.propagate = False

    syslog_path = "/dev/log" if os.path.exists("/dev/log") else "/var/run/syslog"
    syslog_handler = logging.handlers.SysLogHandler(
        address=syslog_path,
        facility=logging.handlers.SysLogHandler.LOG_AUTH,
    )
    formatter = logging.Formatter("%(name)s: %(message)s")
    syslog_handler.setFormatter(formatter)

    auth_logger.addHandler(syslog_handler)
    auth_logger._syslog_configured = True  # type: ignore[attr-defined]
