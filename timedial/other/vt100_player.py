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

import os
import shutil
import sys
import time

DIR = "/opt/demos/vt100"
files = sorted(os.listdir(DIR))

naughty_list = ["dirty.vt", "dogs.vt", "safesex.vt", "monkey.vt", "startrek.vt"]

# Max width 120 columns for readability
term_width = min(shutil.get_terminal_size((80, 20)).columns, 120)
term_lines = shutil.get_terminal_size((80, 20)).lines

entries = [f"{i + 1}. {file}" for i, file in enumerate(files) if file not in naughty_list]
max_width = max(len(entry.replace(".vt", "")) for entry in entries) + 2  # Add spacing
columns = max(1, term_width // max_width)

# Warn about terminal
if os.getenv("TERM", "").lower() != "vt100":
    print("Note: these animations work best on a VT100 terminal!")

slow: bool | None = None
while slow is None:
    response = input("Slow down to 9600 baud? [Y/n]: ").strip().lower()
    if response == "y" or response == "":
        slow = True
    elif response == "n":
        slow = False


def print_list() -> None:
    """Prints the list of available animation files in columns.

    The function displays entries in column-major order, based on
    terminal width and filtered from a naughty_list. Entries are
    formatted to align evenly in the terminal.
    """
    rows = (len(entries) + columns - 1) // columns
    for row in range(rows):
        for col in range(columns):
            index = col * rows + row
            if index < len(entries):
                print(entries[index].replace(".vt", "").ljust(max_width), end="")
        print()


def print_animation(file: str) -> None:
    """Plays a VT100-style animation from a file.

    Clears the terminal and displays the contents of a .vt file
    character by character, simulating terminal output. Optionally
    slows the output to approximate 9600 baud speed.

    Args:
        file: The filename of the .vt animation to be displayed.
    """
    os.system("clear")
    with open(os.path.join(DIR, file), "br") as f:
        data = f.read()

    try:
        for char in data:
            sys.stdout.buffer.write(bytes([char]))
            sys.stdout.flush()
            if slow:
                time.sleep(1 / (9600 // 10))
    except KeyboardInterrupt:
        pass

    sys.stdout.write("\033(B")  # ASCII charset
    sys.stdout.write("\033[0m")  # Reset colors
    sys.stdout.write("\033[?25h")  # Show cursor
    sys.stdout.write("\033[24;1H")  # Move cursor to bottom
    sys.stdout.write("\033#5")  # Normal line width
    sys.stdout.flush()
    print("Press enter to continue...", end="")
    input()
    os.system("reset")


def main() -> None:
    """Runs the main loop of the TimeDial animation viewer.

    Repeatedly prompts the user to select a VT100 animation file to play.
    Handles input validation, displays available options, and respects the
    naughty list for restricted files.

    The loop continues until the user enters '0' to exit.
    """
    while True:
        os.system("clear")
        print_list()
        request = input("\nMake a chocie, 0 to exit > ")
        if not request.isdigit():
            print(f"Enter a number from 1 to {len(files)}")
            continue
        if request == "0":
            exit()
        print()
        if files[int(request) - 1] in naughty_list:
            print("")
            while True:
                response = (
                    input(f"The file: {files[int(request) - 1]} is on the naughty list. Are you sure you want to continue? [y/N]: ")
                    .strip()
                    .lower()
                )
                if response == "y":
                    print_animation(files[int(request) - 1])
                    break
                elif response == "n" or response == "":
                    break
        else:
            print_animation(files[int(request) - 1])


if __name__ == "__main__":
    main()
