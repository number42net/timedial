import curses
import logging
import os
import textwrap
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

LOG_COORDINATES = False


class Window(ABC):
    _size_x = 0
    _size_y = 0
    _pos_x = 0
    _pos_y = 0
    _min_tsize_x = 0
    _min_tsize_y = 0

    def __init__(self, tdscr: curses.window, name: str):
        self.tdscr = tdscr
        self.name = name

        self._verify_term_size()
        self._position()
        self._log_coordinates()

        self._win = curses.newwin(self._size_y, self._size_x, self._pos_y, self._pos_x)

    def _verify_term_size(self, min_x: int = 40, min_y: int = 24) -> bool:
        self._tsize_y, self._tsize_x = self.tdscr.getmaxyx()
        if self._tsize_y < min_y or self._tsize_x < min_x:
            return False

        return True

    def refresh(self) -> None:
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
        if LOG_COORDINATES:
            logger.debug(f"{self.name} Terminal size: {self._tsize_x}, {self._tsize_y}")
            logger.debug(f"{self.name} Window size: {self._size_x}, {self._size_y}")
            logger.debug(f"{self.name} Window pos: {self._pos_x}, {self._pos_y}")

    @abstractmethod
    def _position(self) -> None:
        pass

    @abstractmethod
    def _generate(self) -> None:
        pass

    def delete(self) -> None:
        self._win.erase()
        self._win.noutrefresh()


class Header(Window):
    def _position(self) -> None:
        self._size_x = self._tsize_x
        self._size_y = 1
        self._pos_x = 0
        self._pos_y = 0

    def _generate(self) -> None:
        # self._win.bkgd(" ", curses.A_REVERSE)
        text = "TimeDial.org"
        self._win.erase()
        self._win.addstr(0, max(0, (self._tsize_x - 1 - len(text)) // 2), text, curses.A_BOLD)
        self._win.noutrefresh()


class Footer(Window):
    def _position(self) -> None:
        self._size_x = self._tsize_x
        self._size_y = 1
        self._pos_x = 0
        self._pos_y = self._tsize_y - 1

    def _generate(self) -> None:
        # self._win.bkgd(" ", curses.A_REVERSE)
        self._win.erase()
        self._win.addstr(0, 1, f"Terminal: {os.getenv('TERM')} ({self._tsize_x}x{self._tsize_y})")
        text = "F1 for help"
        self._win.addstr(0, self._tsize_x - len(text) - 1, text)
        self._win.noutrefresh()


class DescriptionBox(Window):
    _entries: list[str] = []

    def _position(self) -> None:
        self._size_x = int(self._tsize_x / 2) - 4
        self._size_y = self._tsize_y - 4
        self._pos_x = int(self._tsize_x / 2) + 2
        self._pos_y = 2

    def _generate(self) -> None:
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
    _entries: list[str] = []
    _last_entries: list[str] = []  # Store last rendered state
    border: bool = False

    def _position(self) -> None:
        self._size_x = min(self._tsize_x - 2, max([len(i) for i in self._entries] + [len(self.name) + 2, 10])) + 2
        self._size_y = min([self._tsize_y - 4, len(self._entries) + 2])
        self._pos_x = int((self._tsize_x - self._size_x) / 2)
        self._pos_y = int((self._tsize_y - self._size_y) / 2) - 1

    def _generate(self) -> None:
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
    _entries: list[str] = []
    selected_index: int = 0

    def _position(self) -> None:
        # The width should be at least 10, or the length of the entries or title
        if self._tsize_x < 80:
            max_size_x = self._tsize_x - 4
        else:
            max_size_x = int(self._tsize_x / 2) - 4
        self._size_x = min(max_size_x, max([len(i) for i in self._entries] + [len(self.name) + 2, 10])) + 4
        self._size_y = min([self._tsize_y - 4, len(self._entries) + 2])
        self._pos_x = 2
        self._pos_y = 2

    def _generate(self) -> None:
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
        self._entries.append(item)

    def clear_enties(self) -> None:
        self._entries = []
        self.selected_index = 0

    def handle_key(self, key: int) -> None:
        old_selection = self.selected_index
        if key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self._entries)
        elif key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self._entries)

        if old_selection != self.selected_index:
            self._win.addstr(old_selection + 1, 2, self._entries[old_selection])
            self._win.addstr(self.selected_index + 1, 2, self._entries[self.selected_index], curses.A_REVERSE)
            self._win.noutrefresh()
