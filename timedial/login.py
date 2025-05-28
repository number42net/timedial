import logging
import os
import subprocess

from timedial.interface import cursed_interface

logging.basicConfig(level=logging.DEBUG)

file_handler = logging.FileHandler("example.log")
file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger()

logger.handlers.clear()
logger.addHandler(file_handler)


def set_terminal() -> None:
    with open("/opt/timedial/supported_terminals") as file:
        supported_terminals = [i.strip() for i in file.readlines()]

    print(
        "Please provide some details about your terminal. If in doubt, "
        "choose xterm-color for a modern terminal emulator, or vt100 or ansi for a vintage terminal"
    )
    print("If you're in doubt about the size, use 80 columns and 24 lines")

    terminal = ""
    while not terminal:
        value = input("Terminal type: ")
        if value in supported_terminals:
            terminal = value
        else:
            print(
                f"Unknown terminal type: '{value}'. If in doubt, "
                "choose xterm-color for a modern terminal emulator, or vt100 or ansi for a vintage terminal"
            )

    cols = ""
    while not cols:
        value = input("Columns: ")
        if not value.isdigit():
            print("Columns needs to be an integer")
        elif not int(value) >= 40:
            print("Minimum size is 40 columns")
        else:
            cols = value

    rows = ""
    while not rows:
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
    subprocess.run(["stty", "rows", rows, "cols", cols], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    try:
        if not os.getenv("TERM"):
            set_terminal()
        cursed_interface.main()
    except KeyboardInterrupt:
        pass
