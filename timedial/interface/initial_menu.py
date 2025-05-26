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

import os
import shutil
import subprocess

from timedial.accounts import account
from timedial.config import config
from timedial.interface.banner import banner
from timedial.interface.menu import MenuItem, load_menu


def goodbye() -> None:
    print("\n\n\nThank you for visting TimeDial.org, hope to see you soon again! \n")
    os.system("pkill -u $(whoami)")


def welcome() -> None:
    """Greet the currently logged-in user."""
    try:
        login_user = subprocess.check_output(["logname"]).decode().strip()
        user = account.read(login_user)

    except Exception as exc:
        print(f"Failed to identify username: {exc}")
        exit(1)

    name = user.realname if user.realname else user.username
    size = shutil.get_terminal_size()
    term_type = os.environ.get("TERM", "unknown")

    print(banner(size.columns))

    print(f"Welcome to TimeDial.org {name}!")
    print(f"Terminal: {term_type}, Columns: {size.columns}, Rows: {size.lines}")
    if config._ephemeral:
        print("\nWARNING: This instances is ephemeral, your data will be lost whenever the instance is restarted!")
    print()


def generate_menu(menu: MenuItem, exit: bool = False) -> MenuItem | None:
    if not menu.items:
        raise Exception("Can only generate a memu on a menu")

    os.system("clear")
    welcome()

    print("Make a choice to go back in time!")

    choices: dict[int, MenuItem] = {}
    for item, data in enumerate(menu.items, start=1):
        if data.command:
            print(f"{item} - {data.name} ({data.command.original_date}/{data.command.version_date} by {data.command.publisher})")
        else:
            print(f"{item} - {data.name}")
        choices[item] = data
    if not exit:
        print("\n0 - Return to main menu")
    else:
        print("\n0 - Disconnect")

    print()
    while True:
        result = input("Choice: ")
        if result == "0" and exit:
            goodbye()
        elif result == "0":
            return None
        elif not result.isdigit() or int(result) not in choices:
            print(f"Not a valid choice: {result}")
        else:
            return choices[int(result)]


def menu() -> None:
    try:
        menu = load_menu()

        result = None
        while True:
            if not result:
                result = generate_menu(menu, exit=True)
            elif result.items:
                result = generate_menu(result)
            elif result.command:
                return_code = os.system(" ".join(result.command.exec))
                if return_code:
                    print(f"Execution resulted in non-zero return value: {return_code}")
                    input("\nPress enter to continue...")
                result = generate_menu(menu, exit=True)

    except KeyboardInterrupt:
        goodbye()
