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
import os
import textwrap
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

LOG_COORDINATES = False


class Window(ABC):
    """Abstract base class for curses-based UI windows."""

    _size_x = 0
    _size_y = 0
    _pos_x = 0
    _pos_y = 0
    _min_tsize_x = 0
    _min_tsize_y = 0

    def __init__(self, tdscr: curses.window, name: str):
        """Initializes a window with terminal screen reference and name.

        Args:
            tdscr (curses.window): The main terminal screen.
            name (str): Name of the window.
        """
        self.tdscr = tdscr
        self.name = name

        self._verify_term_size()
        self._position()
        self._log_coordinates()

        self._win = curses.newwin(self._size_y, self._size_x, self._pos_y, self._pos_x)

    def _verify_term_size(self, min_x: int = 40, min_y: int = 24) -> bool:
        """Checks if terminal size meets the minimum required dimensions.

        Args:
            min_x (int): Minimum width required. Defaults to 40.
            min_y (int): Minimum height required. Defaults to 24.

        Returns:
            bool: True if terminal size is adequate, False otherwise.
        """
        self._tsize_y, self._tsize_x = self.tdscr.getmaxyx()
        if self._tsize_y < min_y or self._tsize_x < min_x:
            return False

        return True

    def refresh(self) -> None:
        """Refreshes the window, re-validates terminal size and re-renders window content."""
        if not self._verify_term_size():
            self.tdscr.noutrefresh()
            self.tdscr.clear()
            self.tdscr.addstr(0, 0, "Terminal too small")
            logger.error(f"Terminal went below minimum size: {self._tsize_x}, {self._tsize_y}")
            return

        self._position()
        self._log_coordinates()
        self._win.erase()
        self._win.noutrefresh()

        self._win.resize(self._size_y, self._size_x)
        self._win.mvwin(self._pos_y, self._pos_x)
        self._win.erase()
        self._win.noutrefresh()
        self._generate()

    def _log_coordinates(self) -> None:
        """Logs the current terminal and window size and position if LOG_COORDINATES logging is enabled."""
        if LOG_COORDINATES:
            logger.debug(f"{self.name} Terminal size: {self._tsize_x}, {self._tsize_y}")
            logger.debug(f"{self.name} Window size: {self._size_x}, {self._size_y}")
            logger.debug(f"{self.name} Window pos: {self._pos_x}, {self._pos_y}")

    @abstractmethod
    def _position(self) -> None:
        """Abstract method to set the window's size and position."""
        pass

    @abstractmethod
    def _generate(self) -> None:
        """Abstract method to generate the content of the window."""
        pass

    def delete(self) -> None:
        """Erases and removes the window from display."""
        self._win.erase()
        self._win.noutrefresh()


class Header(Window):
    """Displays a header bar at the top of the terminal screen."""

    def _position(self) -> None:
        """Sets size and position of the header window."""
        self._size_x = self._tsize_x
        self._size_y = 1
        self._pos_x = 0
        self._pos_y = 0

    def _generate(self) -> None:
        """Generates and renders the header content."""
        text = "TimeDial.org"
        self._win.erase()
        self._win.addstr(0, max(0, (self._tsize_x - 1 - len(text)) // 2), text, curses.A_BOLD)
        self._win.noutrefresh()


class Footer(Window):
    """Displays a footer / status bar at the bottom of the terminal screen."""

    def _position(self) -> None:
        """Sets size and position of the footer window."""
        self._size_x = self._tsize_x
        self._size_y = 1
        self._pos_x = 0
        self._pos_y = self._tsize_y - 1

    def _generate(self) -> None:
        """Generates and renders the footer content."""
        # self._win.bkgd(" ", curses.A_REVERSE)
        self._win.erase()
        self._win.addstr(0, 1, f"Terminal: {os.getenv('TERM')} ({self._tsize_x}x{self._tsize_y})")
        text = "F1 for help"
        self._win.addstr(0, self._tsize_x - len(text) - 1, text)
        self._win.noutrefresh()


class DescriptionBox(Window):
    """Displays multi-line descriptions in a bordered box."""

    def __init__(self, tdscr: curses.window, name: str) -> None:
        """Initializes the DescriptionBox window.

        Args:
            tdscr (curses.window): The main terminal screen.
            name (str): The name of the window, displayed as the title.
        """
        self._entries: list[str] = []
        super().__init__(tdscr, name)

    def _position(self) -> None:
        """Displays multi-line descriptions in a bordered box."""
        self._size_x = int(self._tsize_x / 2) - 4
        self._size_y = self._tsize_y - 4
        self._pos_x = int(self._tsize_x / 2) + 2
        self._pos_y = 2

    def _generate(self) -> None:
        """Generates and renders description text entries, wrapped to fit the window."""
        if not self._verify_term_size(80):
            return

        self._win.erase()
        self._win.border()
        # Title
        self._win.addstr(0, 2, f" {self.name} ")

        # Entries
        y = 1
        for entry in self._entries:
            # Handle empty lines
            if not entry:
                y += 1
                continue

            wrapped_lines = textwrap.wrap(entry, self._size_x - 4)
            for line in wrapped_lines:
                if y < self._size_y - 1:  # Prevent writing beyond window height
                    self._win.addstr(y, 2, line)
                    y += 1
                else:
                    break  # Avoid overflow

        self._win.noutrefresh()


class TextBox(Window):
    """Displays static text lines with optional borders."""

    def __init__(self, tdscr: curses.window, name: str) -> None:
        """Initializes the TextBox window.

        Args:
            tdscr (curses.window): The main terminal screen.
            name (str): The name of the window, used as a title if border is enabled.
        """
        self._entries: list[str] = []
        self._last_entries: list[str] = []  # Store last rendered state
        self.border: bool = False
        super().__init__(tdscr, name)

    def _position(self) -> None:
        """Sets size and position of the text box based on its contents."""
        self._size_x = min(self._tsize_x - 2, max([len(i) for i in self._entries] + [len(self.name) + 2, 10])) + 2
        self._size_y = min([self._tsize_y - 4, len(self._entries) + 2])
        self._pos_x = int((self._tsize_x - self._size_x) / 2)
        self._pos_y = int((self._tsize_y - self._size_y) / 2) - 1

    def _generate(self) -> None:
        """Generates and renders text lines, only updating lines that have changed."""
        if self.border:
            self._win.border()
            self._win.addstr(0, 0, f" {self.name} ")

        offset = 2 if self.border else 0

        for line, entry in enumerate(self._entries):
            # Only redraw line if it's changed
            if line >= len(self._last_entries) or entry != self._last_entries[line]:
                self._win.move(line + 1, offset)
                self._win.clrtoeol()
                self._win.addstr(line + 1, offset, entry)

        self._last_entries = self._entries.copy()
        self._win.noutrefresh()


class Menu(Window):
    """Displays a selectable list of menu items with cursor navigation support."""

    def __init__(self, tdscr: curses.window, name: str) -> None:
        """Initializes the Menu window.

        Args:
            tdscr (curses.window): The main terminal screen.
            name (str): The name of the window, used as the menu title.
        """
        self._entries: list[str] = []
        self.selected_index: int = 0
        super().__init__(tdscr, name)

    def _position(self) -> None:
        """Sets size and position of the menu window based on its entries."""
        if self._tsize_x < 80:
            max_size_x = self._tsize_x - 4
        else:
            max_size_x = int(self._tsize_x / 2) - 4
        self._size_x = min(max_size_x, max([len(i) for i in self._entries] + [len(self.name) + 2, 10])) + 4
        self._size_y = min([self._tsize_y - 4, len(self._entries) + 2])
        self._pos_x = 2
        self._pos_y = 2

    def _generate(self) -> None:
        """Generates and renders menu items, highlighting the selected one."""
        self._win.erase()
        self._win.border()
        # Title
        self._win.addstr(0, 2, f" {self.name} ")

        # Entries
        for line, entry in enumerate(self._entries, start=0):
            if line == self.selected_index:
                self._win.addstr(line + 1, 2, entry, curses.A_REVERSE)
            else:
                self._win.addstr(line + 1, 2, entry)

        self._win.noutrefresh()

    def add_entry(self, item: str) -> None:
        """Adds a new item to the menu.

        Args:
            item (str): The menu item text to add.
        """
        self._entries.append(item)

    def clear_enties(self) -> None:
        """Clears all menu entries and resets selection index."""
        self._entries = []
        self.selected_index = 0

    def handle_key(self, key: int) -> None:
        """Handles key input to navigate menu items.

        Args:
            key (int): The input key code (e.g., curses.KEY_UP or curses.KEY_DOWN).
        """
        old_selection = self.selected_index
        if key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self._entries)
        elif key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self._entries)

        if old_selection != self.selected_index:
            self._win.addstr(old_selection + 1, 2, self._entries[old_selection])
            self._win.addstr(self.selected_index + 1, 2, self._entries[self.selected_index], curses.A_REVERSE)
            self._win.noutrefresh()
