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

import datetime
import logging
import os
import re
import subprocess
import time

from timedial.config import config
from timedial.logger import daemon_logger_config

daemon_logger_config()
logger = logging.getLogger("timedial.stats")


def list_dir(path: str, extensions: bool = True) -> str:
    """Lists the contents of a directory as a newline-separated string.

    Args:
        path (str): Path to the directory.
        extensions (bool): If False, strips file extensions.

    Returns:
        str: Newline-separated list of filenames (or basenames if extensions is False).
    """
    data = sorted(os.listdir(path))
    if not extensions:
        data = [os.path.splitext(i)[0] for i in data]
    return "\n".join(data)


def execute(command: str | list[str]) -> str:
    """Executes a shell command and returns its output.

    Args:
        command (str): The command to execute (e.g., '/usr/bin/w').

    Returns:
        str: The standard output from the command, or an error message if it fails.
    """
    env = os.environ.copy()
    env["COLUMNS"] = "300"  # set desired terminal width
    env["LINES"] = "100"  # optional, if needed

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
        return mask_ips(result.stdout)

    except subprocess.CalledProcessError as e:
        msg = f"Error executing 'w': {e}"
        logger.error(msg)
        return msg


def write_file(filename: str, content: str) -> None:
    """Writes content to a file within the configured stats directory.

    Args:
        filename (str): The name of the file to write to.
        content (str): The content to write into the file.

    Returns:
        None
    """
    path = os.path.join(config.stats_dir, filename)
    try:
        with open(path, "w") as f:
            f.write(f"Generated on: {datetime.datetime.now().isoformat()}\n\n")
            f.write(content)
    except Exception as exc:
        logger.error(f"Failed to write: {path} - {exc}")


def mask_ips(text: str) -> str:
    """Mask the last two octets of all IPv4 addresses found in the input text.

    Each IP address in the format A.B.C.D will be transformed to A.B.***.***

    Args:
        text (str): The input string potentially containing IPv4 addresses.

    Returns:
        str: The input string with IP addresses masked in the last two octets.
    """
    # Regex to match IPv4 addresses
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

    def mask(match: re.Match[str]) -> str:
        """Replace the last two octets of an IPv4 address with asterisks.

        Args:
            match (re.Match): A regex match object for an IP address.

        Returns:
            str: The masked IP address.
        """
        ip = match.group()
        parts = ip.split(".")
        parts[2] = "***"
        parts[3] = "***"
        return ".".join(parts)

    return re.sub(ip_pattern, mask, text)


def main() -> None:
    """Run through all files."""
    while True:
        try:
            write_file("w.txt", execute("/usr/bin/w"))
            write_file("last.txt", execute("/usr/bin/last"))
            write_file("top_cpu.txt", execute(["/usr/bin/top", "-b", "-o", "%CPU", "-n", "1", "-c"]))
            write_file("top_mem.txt", execute(["/usr/bin/top", "-b", "-o", "%CPU", "-n", "1", "-c"]))
            write_file("user_list.txt", list_dir("/data/guests", extensions=False))
        except Exception as exc:
            logger.exception(f"Encountered error during run: {exc}")

        time.sleep(60)
