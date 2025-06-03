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
import subprocess
import sys
import termios

from timedial.interface import cursed_interface
from timedial.logger import ui_logger_config

ui_logger_config()
root_logger = logging.getLogger("timedial")
logger = logging.getLogger("timedial.login")


def set_terminal() -> None:
    """Prompts the user to manually configure terminal type and dimensions.

    Sets the TERM, LINES, and COLUMNS environment variables based on user input,
    and attempts to apply the configuration using the `stty` command.

    Logs and prints error messages if the configuration fails.
    """
    with open("/opt/timedial/supported_terminals") as file:
        supported_terminals = [i.strip() for i in file.readlines()]

    print(
        "\nPlease provide some details about your terminal. If in doubt choose xterm-color\n"
        "for a modern terminal emulator, or vt100 or ansi for a vintage terminal."
    )
    print("\nIf you're in doubt about the size, use 80 columns and 24 lines.\n")

    terminal = ""
    while not terminal:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        value = input("Terminal type: ")
        if value in supported_terminals:
            terminal = value
        else:
            print(f"Unknown terminal type: '{value}'.")

    cols = ""
    while not cols:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        value = input("Columns: ")
        if not value.isdigit():
            print("Columns needs to be an integer")
        elif not int(value) >= 40:
            print("Minimum size is 40 columns")
        else:
            cols = value

    rows = ""
    while not rows:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        value = input("Rows: ")
        if not value.isdigit():
            print("Rows needs to be an integer")
        elif not int(value) >= 24:
            print("Minimum size is 24 rows")
        else:
            rows = value

    os.environ["TERM"] = terminal
    os.environ["LINES"] = rows
    os.environ["COLUMNS"] = cols
    try:
        subprocess.run(
            ["stty", "rows", rows, "cols", cols],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        msg = f"Failed to set terminal using stty: {exc}\nstdout: {exc.stdout.strip()}\nstderr: {exc.stderr.strip()}"
        logger.error(msg)
        print(msg)
    except Exception as exc:
        msg = f"Failed to set terminal using stty: {exc}"
        logger.error(msg, exc_info=True)
        print(msg)


def main() -> None:
    """Main entry point for TimeDial.

    Checks and sets terminal environment variables if not already defined,
    clears the screen, and launches the curses-based interface.

    Handles keyboard interrupts and logs unexpected exceptions.
    """
    try:
        term = os.getenv("TERM")
        if not term:
            logger.warning("Logged in without $TERM")
            set_terminal()
        else:
            logger.info(f"Logged in with: {term}")
        os.system("clear")
        cursed_interface.main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        msg = f"Uncaught exception: {exc}"
        root_logger.error(msg, exc_info=True)
        print(msg)
