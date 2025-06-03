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

import curses
import logging
import mailbox
import os
import time
from typing import TypeVar

from timedial.accounts import account
from timedial.interface import MENU_CALLABLES, cursed
from timedial.interface.menu_data import MainMenu, MenuItem, load_menu

logger = logging.getLogger(__name__)
banner = ((),)


help = [
    " _____ _                ____  _       _ ",
    "|_   _(_)_ __ ___   ___|  _ \(_) __ _| |",
    "  | | | | '_ ` _ \ / _ \ | | | |/ _` | |",
    "  | | | | | | | | |  __/ |_| | | (_| | |",
    "  |_| |_|_| |_| |_|\___|____/|_|\__,_|_|",
    "",
    "Travel through time with our collection",
    "of apps, shells, games, and simulators.",
    "",
    "----------------------------------------",
    "",
    "   - Use ARROW KEYS to move",
    "   - Press ENTER to select",
    "   - Press F1 for help",
    "",
    "----------------------------------------",
    "",
    "     Enjoy your trip through time!",
]

T = TypeVar("T", bound=cursed.Window)


class Menu:
    """Handles the display and navigation of a menu system within a curses-based UI."""

    def __init__(self, menu_window: cursed.Menu, description_window: cursed.DescriptionBox) -> None:
        """Initializes the Menu with given menu and description windows.

        Args:
            menu_window (cursed.Menu): The window displaying the menu entries.
            description_window (cursed.DescriptionBox): The window displaying item descriptions.
        """
        self.menu = menu_window
        self.description = description_window
        self.data = load_menu()
        self.history: list[tuple[MenuItem | MainMenu, int]] = []

        self.display_menu(self.data)

    def display_menu(self, menu_data: MainMenu | MenuItem | None = None, location: int = 0) -> None:
        """Displays the menu and populates it with entries.

        Args:
            menu_data (MainMenu | MenuItem | None): The menu data to display. Defaults to the main menu.
            location (int): The index of the selected menu item. Defaults to 0.
        """
        self.menu.clear_enties()
        if not menu_data:
            menu_data = self.data
        if not menu_data.items:
            return

        for item in menu_data.items:
            self.menu.add_entry(item.name)

        self.menu.selected_index = location

        self.current_data = menu_data
        self.current_item = menu_data.items[location]
        self.update_description()

        self.menu.refresh()

    def handle_key(self, key: int) -> None:
        """Handles keyboard input for menu navigation and selection.

        Args:
            key (int): The key code input by the user.
        """
        if key == curses.KEY_UP or key == curses.KEY_DOWN:
            self.menu_move(key)
            curses.doupdate()

        elif key == 10 and self.current_item.items:
            self.history.append((self.current_data, self.menu.selected_index))
            self.display_menu(self.current_item)
            curses.doupdate()

        elif key == 10 and self.current_item.command:
            self.execute()

        elif key == 10 and self.current_item.callable:
            self.history.append((self.current_data, self.menu.selected_index))
            self.display_menu(MENU_CALLABLES[self.current_item.callable]())
            curses.doupdate()

        elif key == 27 or key == curses.KEY_LEFT:
            if self.history:
                prev_data, prev_index = self.history.pop()
                self.display_menu(prev_data, prev_index)
                curses.doupdate()
            else:
                logger.debug("No previous menu to return to.")

        else:
            logger.debug(f"Unknown key: {key}")

    def menu_move(self, key: int) -> None:
        """Moves the menu selection based on the key input.

        Args:
            key (int): The key code for moving selection (typically arrow keys).
        """
        self.menu.handle_key(key)
        if not self.current_data.items:
            return

        self.current_item = self.current_data.items[self.menu.selected_index]
        self.update_description()

    def update_description(self) -> None:
        """Updates the description box with information about the currently selected menu item."""
        if not isinstance(self.current_item.description, list):
            self.description._entries = [self.current_item.description, ""]
        else:
            # self.description._entries = list(self.current_item.description)
            self.description._entries = (
                [s for item in self.current_item.description[:-1] for s in (item, "")] + [self.current_item.description[-1]] + [""]
            )

        if self.current_item.command:
            desc = []
            if self.current_item.command.publisher:
                desc.append(f"Original publisher: {self.current_item.command.publisher}")
            if self.current_item.command.version and self.current_item.command.version_date:
                desc.append(f"Version: {self.current_item.command.version} ({self.current_item.command.version_date})")
            elif self.current_item.command.version:
                desc.append(f"Version: {self.current_item.command.version}")
            if self.current_item.command.original_date:
                desc.append(f"First release: {self.current_item.command.original_date}")
            self.description._entries += desc

        self.description.refresh()

    def execute(self) -> None:
        """Executes the command associated with the selected menu item, if any."""
        command = self.current_item.command
        if not command:
            logger.info(command)
            return
        curses.endwin()

        return_code = os.system(" ".join(command.exec))
        if return_code:
            print(f"Execution resulted in non-zero return value: {return_code}")
            input("\nPress enter to continue...")

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)


class CursedInterface:
    """Main interface class for handling a full-screen curses-based UI."""

    def __init__(self, tdscr: curses.window) -> None:
        """Initializes the curses interface and sets up initial windows.

        Args:
            tdscr (curses.window): The main terminal screen window.
        """
        self.account_data = account.read()
        self._all_windows: list[cursed.Window] = []
        self._tdscr = tdscr
        try:
            curses.curs_set(0)
        except curses.error:
            pass  # Terminal doesn't support hiding the cursor

        self._tdscr.refresh()

        self.header_window = self.add_window(cursed.Header, "header")
        self.header_window.refresh()

        self.footer_window = self.add_window(cursed.Footer, "footer")
        self.footer_window.update(self.check_mail())
        self.footer_window.refresh()

        self.welcome_screen()
        self.menu_interface()

    def welcome_screen(self) -> None:
        """Displays the welcome/help screen with usage instructions."""
        window = self.add_window(cursed.TextBox, "Welcome")
        window._entries = help
        window.refresh()
        curses.doupdate()
        self._tdscr.getch()
        self.remove_window(window)

    def menu_interface(self) -> None:
        """Initializes and displays the main menu interface."""
        self.description_window = self.add_window(cursed.DescriptionBox, "Description")
        self.menu_window = self.add_window(cursed.Menu, "Main menu")
        self.menu_handler = Menu(self.menu_window, self.description_window)
        curses.doupdate()

        self._active_window = self.menu_handler
        self.handle_keys()

    def handle_keys(self) -> None:
        """Continuously listens for and processes key inputs."""
        last_status_update = time.time()
        while True:
            if time.time() - last_status_update > 30:
                self.footer_window.update(self.check_mail())
                last_status_update = time.time()

            key = self._tdscr.getch()
            if key == curses.KEY_RESIZE:
                self._tdscr.clear()
                curses.update_lines_cols()
                self._tdscr.refresh()
                for window in self._all_windows:
                    window.refresh()
                curses.doupdate()
            elif key == curses.KEY_F1:
                self.welcome_screen()
                self._tdscr.refresh()
                for window in self._all_windows:
                    window.refresh()
                curses.doupdate()

            elif self._active_window:
                self._active_window.handle_key(key)

    def add_window(self, windowclass: type[T], name: str) -> T:
        """Adds and initializes a new window to the interface.

        Args:
            windowclass (type[T]): The class of the window to create.
            name (str): The name identifier for the window.

        Returns:
            T: An instance of the created window.
        """
        tmp = windowclass(self._tdscr, name)
        self._all_windows.append(tmp)
        return tmp

    def remove_window(self, window: cursed.Window) -> None:
        """Removes and deletes a window from the interface.

        Args:
            window (cursed.Window): The window to remove.
        """
        window.delete()
        self._all_windows.remove(window)

    def check_mail(self) -> int:
        """Count the number of unread emails for the current user.

        This method opens the user's mailbox located at /var/mail/{username}
        and iterates through the messages. A message is considered unread
        if the 'Status' header does not contain the letter 'R'.

        Returns:
            int: The number of unread email messages.

        Raises:
            None: Silently ignores FileNotFoundError if the mailbox file doesn't exist.
        """
        unread_counter = 0
        try:
            mbox = mailbox.mbox(f"/var/mail/{self.account_data.username}")
            for message in mbox:
                status = message.get("Status", "")
                if "R" not in status:  # If 'R' is not present, it's unread
                    unread_counter += 1
        except FileNotFoundError:
            pass
        except Exception as exc:
            logger.exception(f"Failed to open mail: {exc}")

        return unread_counter


def main() -> None:
    """Entry point for launching the curses interface."""
    curses.wrapper(CursedInterface)
