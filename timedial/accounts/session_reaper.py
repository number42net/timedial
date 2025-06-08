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

import json
import logging
import os
import signal
import time
from typing import Any

import psutil

from timedial.config import config
from timedial.logger import auth_logger_config

auth_logger_config()
logger = logging.getLogger("timedial.reaper")


def log_dict(d: dict[str, Any], max_size: int = 512, prefix: str = "Chunk") -> None:
    """Logs a dictionary in JSON-serializable chunks, split by key groups.

    This function iterates through a dictionary and logs key-value pairs in
    chunks that do not exceed a specified maximum byte size. It ensures that
    no chunk splits an individual key-value pair, making each log entry
    a valid JSON object. Useful for logging large dicts (e.g., psutil data)
    in environments like BusyBox syslog, which truncate oversized messages.

    Args:
        d (dict[str, Any]): The dictionary to be logged.
        max_size (int): Maximum size (in bytes) of each log message.
            Default is 480, safe for syslog systems like BusyBox.
        prefix (str): A prefix for each log message to identify the chunk group.
            Defaults to "Proc info chunk".

    Returns:
        None
    """
    current: dict[str, Any] = {}
    current_size = 0
    chunk_index = 1

    for k, v in d.items():
        try:
            item_json = json.dumps({k: v}, default=str)
        except Exception:
            item_json = json.dumps({k: str(v)})

        if current_size + len(item_json) > max_size:
            logger.info("%s %d: %s", prefix, chunk_index, json.dumps(current, default=str))
            chunk_index += 1
            current = {}
            current_size = 0

        current[k] = v
        current_size += len(item_json)

    if current:
        logger.info("%s %d: %s", prefix, chunk_index, json.dumps(current, default=str))


def kill_processes_by_user(user: psutil._common.suser, signal_type: int = signal.SIGTERM) -> None:
    """Kill all processes for a given user, regardless of TTY.

    Args:
        user (psutil._common.suser): The user whose processes should be killed.
        signal_type (int, optional): The signal to send (default is SIGTERM).
    """
    count = 0
    for proc in psutil.process_iter(["pid", "username"]):
        try:
            if proc.info["username"] == user.name:
                logger.info(f"Killing PID {proc.pid} (user: {user.name}) because it has no terminal. Proc info: {proc.as_dict()}")
                proc.send_signal(signal_type)
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as exc:
            logger.error(f"Failed to kill process {proc.pid}: {exc}")
    logger.info(f"Killed {count} non-TTY processes for user: {user.name}")


def kill_processes_on_tty(user: psutil._common.suser, signal_type: int = signal.SIGTERM) -> None:
    """Kill all processes associated with the user's terminal (TTY).

    Args:
        user (psutil._common.suser): The user session whose processes should be killed.
        signal_type (int, optional): The signal to send (default is SIGTERM).
    """
    count = 0
    for proc in psutil.process_iter(["pid", "terminal"]):
        try:
            if proc.info["terminal"] and proc.info["terminal"] == f"/dev/{user.terminal}":
                logger.info(f"Killing PID {proc.pid} on {proc.info['terminal']}.")
                log_dict(proc.as_dict())

                proc.send_signal(signal_type)
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as exc:
            logger.error(f"Failed to kill process {proc.pid} for : {exc}")
    logger.info(f"Killed {count} processes for: {user.name} {user.terminal}")


def check_idle(user: psutil._common.suser) -> bool:
    """Check whether a user's session has been idle beyond the configured threshold.

    Args:
        user (psutil._common.suser): The user session to check.

    Returns:
        bool: True if the session has been idle too long, False otherwise.
    """
    tty = user.terminal
    tty_path = f"/dev/{tty}"
    try:
        atime = os.stat(tty_path).st_atime
    except FileNotFoundError:
        logger.warning(f"Failed to get stat for: {user.name} {tty}")
        return False

    idle_seconds = int(time.time() - atime)
    if idle_seconds > config.max_idle_session:
        logger.info(f"Identified session for user: {user.name} {tty} that has been idle for: {idle_seconds} seconds")
        return True

    return False


def main() -> None:
    """Main routine for the idle session reaper.

    Iterates through all current user sessions. If any session for a user
    lacks a proper TTY, all processes for that user are killed. Otherwise,
    only idle sessions are reaped.
    """
    while True:
        sessions = psutil.users()
        users_with_no_tty = set()
        handled_users = set()

        # Identify users who have any session with no or invalid TTY
        for session in sessions:
            if not session.terminal or not session.terminal.startswith("pts/"):
                users_with_no_tty.add(session.name)

        # Now iterate and act once per user
        for session in sessions:
            if session.name in handled_users:
                continue

            if session.name in users_with_no_tty:
                logger.info(f"User {session.name} has a non-PTY session. Killing all their processes.")
                kill_processes_by_user(session)
            elif check_idle(session):
                kill_processes_on_tty(session)

            handled_users.add(session.name)

        time.sleep(1)


if __name__ == "__main__":
    main()
