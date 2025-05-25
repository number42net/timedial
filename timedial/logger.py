"""TimeDial project.

Copyright (c) 2025 Martin Miedema
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

logger = logging.getLogger("timedial")
logger.setLevel(logging.DEBUG)

# Only configure once
if not getattr(logger, "_syslog_configured", False):
    syslog_path = "/dev/log" if os.path.exists("/dev/log") else "/var/run/syslog"

    syslog_handler = logging.handlers.SysLogHandler(
        address=syslog_path,
        facility=logging.handlers.SysLogHandler.LOG_AUTH,
    )
    formatter = logging.Formatter("%(name)s: %(levelname)s %(message)s")
    syslog_handler.setFormatter(formatter)

    logger.addHandler(syslog_handler)
    # We could use a custom logging class for this, but MyPy doesn't understand logging.setLoggerClass(CustomLogger) anyway
    logger._syslog_configured = True  # type: ignore[attr-defined]
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced CustomLogger under the 'timedial' logger hierarchy.

    Ensures the logger inherits from the configured 'timedial' base logger,
    including syslog handler and formatting.

    Args:
        name (str): Sub-logger name (e.g., module or component name).

    Returns:
        CustomLogger: A logger instance named 'timedial.<name>'.

    """
    return logging.getLogger(f"timedial.{name}")
