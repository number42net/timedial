import curses
import logging
import os
from typing import TypeVar

from timedial.interface import cursed
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
    def __init__(self, menu_window: cursed.Menu, description_window: cursed.DescriptionBox) -> None:
        self.menu = menu_window
        self.description = description_window
        self.data = load_menu()
        self.previous_menu: MainMenu | MenuItem = self.data
        self.previous_menu_location = 0

        self.display_menu(self.data)

    def display_menu(self, menu_data: MainMenu | MenuItem | None = None, location: int = 0) -> None:
        self.menu.clear_enties()
        if not menu_data:
            menu_data = self.data
        if not menu_data.items:
            return

        for item in menu_data.items:
            self.menu.add_entry(item.name)

        self.menu.selected_index = location

        self.current_data = menu_data
        self.current_item = menu_data.items[0]
        self.update_description()

        self.menu.refresh()

    def handle_key(self, key: int) -> None:
        if key == curses.KEY_UP or key == curses.KEY_DOWN:
            self.menu_move(key)
            curses.doupdate()
        elif key == 10 and self.current_item.items:  # and self.current_item.items[self.menu.selected_index].items:
            self.previous_menu = self.current_data
            self.previous_menu_location = self.menu.selected_index
            self.display_menu(self.current_item)
            curses.doupdate()
        elif key == 10:
            logger.info("Test")
            self.execute()
        elif key == 27 or key == curses.KEY_LEFT:
            self.display_menu(self.previous_menu, self.previous_menu_location)
        else:
            logger.debug(f"Unknown key: {key}")

    def menu_move(self, key: int) -> None:
        self.menu.handle_key(key)
        if not self.current_data.items:
            return

        self.current_item = self.current_data.items[self.menu.selected_index]
        self.update_description()

    def update_description(self) -> None:
        if not isinstance(self.current_item.description, list):
            self.description._entries = [self.current_item.description]
        else:
            self.description._entries = list(self.current_item.description)

        if self.current_item.command:
            self.description._entries += [
                "",
                f"Publisher: {self.current_item.command.publisher}",
                f"Version: {self.current_item.command.version} ({self.current_item.command.version_date})",
                f"First release: {self.current_item.command.original_date}",
            ]

        self.description.refresh()

    def execute(self) -> None:
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
    def __init__(self, tdscr: curses.window) -> None:
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
        self.footer_window.refresh()

        self.welcome_screen()
        self.menu_interface()

    def welcome_screen(self) -> None:
        window = self.add_window(cursed.TextBox, "Welcome")
        window._entries = help
        window.refresh()
        curses.doupdate()
        self._tdscr.getch()
        self.remove_window(window)

    def menu_interface(self) -> None:
        self.description_window = self.add_window(cursed.DescriptionBox, "Description")
        self.menu_window = self.add_window(cursed.Menu, "Main menu")
        self.menu_handler = Menu(self.menu_window, self.description_window)
        curses.doupdate()

        self._active_window = self.menu_handler
        self.handle_keys()

    def handle_keys(self) -> None:
        while True:
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
        tmp = windowclass(self._tdscr, name)
        self._all_windows.append(tmp)
        return tmp

    def remove_window(self, window: cursed.Window) -> None:
        window.delete()
        self._all_windows.remove(window)


def main() -> None:
    curses.wrapper(CursedInterface)
