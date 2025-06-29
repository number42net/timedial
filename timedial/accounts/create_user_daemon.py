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

import argparse
import logging
import os
import re
import subprocess
import time
from pathlib import Path

from watchdog.events import DirCreatedEvent, FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from timedial.accounts import account
from timedial.config import config
from timedial.logger import auth_logger_config

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")

auth_logger_config()
logger = logging.getLogger("timedial.crd")

parser = argparse.ArgumentParser()
parser.add_argument("--no-home-dir", action="store_true", help="If set, do not create the home directory.")

args = parser.parse_args()


def process_file(path: str) -> None:
    """Create a user if the username (derived from the filename) does not already exist.

    Args:
        path (str): The full path to the JSON file containing guest info.

    """
    username = Path(path).stem
    userdata = account.read(username)

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
        logger.info(f"Creating group: {username}")
        subprocess.run(
            [
                "groupadd",
                "-g",
                str(userdata.id[1]),
                username,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create group {username}: {e}")

    if args.no_home_dir:
        try:
            logger.info(f"Creating user: {username}")
            subprocess.run(
                [
                    "useradd",
                    "-M",
                    "-s",
                    "/usr/sbin/nologin",
                    "-u",
                    str(userdata.id[0]),
                    "-g",
                    str(userdata.id[1]),
                    "-G",
                    "guestusers",
                    username,
                ],
                check=True,
            )
            return
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create user {username}: {e}")

    try:
        logger.info(f"Creating user: {username}")
        subprocess.run(
            [
                "useradd",
                "-m",
                "-k",
                "/etc/skel-guest",
                "-s",
                "/usr/local/bin/timedial-login",
                "-u",
                str(userdata.id[0]),
                "-g",
                str(userdata.id[1]),
                "-G",
                "guestusers",
                username,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create user {username}: {e}")

    try:
        maildir = Path(os.path.join(os.path.expanduser(f"~{username}"), "Maildir"))
        if maildir.exists() and not maildir.is_dir():
            logger.warning(f"Maildir: {maildir} exists, but is not a directory!")
            maildir.unlink()  # Deletes file, symlink, etc.
        if not maildir.exists():
            os.mkdir(maildir)
        os.chown(maildir, userdata.id[0], userdata.id[1])
        os.chmod(maildir, 0o700)
    except Exception as exc:
        logger.error(f"Failed to create maildir: {maildir}: {exc}")

    try:
        logger.info(f"Set user file ownership: {username}")
        subprocess.run(["chown", f"{username}:guest", path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set ownership for user file {username}: {e}")


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
    Path(config.guest_dir).mkdir(parents=True, exist_ok=True)

    # Process existing files on startup
    for entry in Path(config.guest_dir).glob("*.json"):
        process_file(str(entry))

    # Set up watchdog observer
    event_handler = GuestFileHandler()
    observer = Observer()
    observer.schedule(event_handler, config.guest_dir, recursive=False)
    observer.start()

    logger.info(f"Monitoring {config.guest_dir} for new guest files.")

    try:
        observer.join()
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        observer.stop()
        observer.join()
        time.sleep(1)
        create_user_daemon()
