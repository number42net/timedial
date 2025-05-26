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
import re
import subprocess
import time
from pathlib import Path

from watchdog.events import DirCreatedEvent, FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

WATCH_DIR = "/data/guests/"
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")

# Set up syslog logging
logger = logging.getLogger("GuestWatcher")
logger.setLevel(logging.INFO)
syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)


def process_file(path: str) -> None:
    """Create a user if the username (derived from the filename) does not already exist.

    Args:
        path (str): The full path to the JSON file containing guest info.

    """
    username = Path(path).stem

    try:
        subprocess.run(
            ["id", username],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.error(f"User already exists: {username}")
        return
    except subprocess.CalledProcessError:
        # User doesn't exist yet
        pass

    try:
        logger.info(f"Creating user: {username}")
        subprocess.run(["useradd", "-M", "-s", "/usr/local/bin/timedial_login", "-G", "guestusers", username], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create user {username}: {e}")

    try:
        logger.info(f"Set user file ownership: {username}")
        subprocess.run(["chown", f"{username}:guest", path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set ownership for user file {username}: {e}")

    try:
        homedir = f"/home/{username}"
        if not os.path.isdir(homedir):
            logger.info(f"Creating home directory: {username}")
            os.mkdir(homedir)

        logger.info(f"Setting home directory permission : {username}")
        os.chmod(homedir, 0o700)
        subprocess.run(["chown", "-R", f"{username}:{username}", homedir], check=True)
    except Exception as e:
        logger.error(f"Failed to set permissions for user file {username}: {e}")


class GuestFileHandler(FileSystemEventHandler):
    """Handle system events and process newly created JSON files."""

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        """Handle newly created files.

        Args:
            event (FileSystemEvent): The event representing file creation.

        """
        if event.is_directory:
            return
        if not str(event.src_path).endswith(".json"):
            return

        process_file(str(event.src_path))


def create_user_daemon() -> None:
    """Start the guest user creation daemon.

    This function sets up a directory watcher using watchdog to monitor
    for new JSON files in a specified directory. For each new file detected,
    it processes the file to create a new system user if the user does not exist.

    The function also ensures the directory exists and processes all existing
    JSON files on startup.
    """
    logger.info("GuestWatcher starting up.")
    Path(WATCH_DIR).mkdir(parents=True, exist_ok=True)

    # Process existing files on startup
    for entry in Path(WATCH_DIR).glob("*.json"):
        process_file(str(entry))

    # Set up watchdog observer
    event_handler = GuestFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    logger.info(f"Monitoring {WATCH_DIR} for new guest files.")

    try:
        observer.join()
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        observer.stop()
        observer.join()
        time.sleep(1)
        create_user_daemon()
