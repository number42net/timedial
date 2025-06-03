"""ASCII player, based on https://github.com/mgracanin/ASCIIStarWars.

ASCII Art (Star Wars) from https://www.asciimation.co.nz/
"""

import curses
import os
import sys
import time

starwars_file_path = "/opt/demos/starwars.txt"

LPF = 14  ## Lines per frame
COLUMNS = 68  # Width of the frame


def main(window: curses.window) -> None:
    """Play the animation."""
    with open(starwars_file_path) as f:
        lines = f.readlines()

    try:
        curses.curs_set(0)
        cursor = False
    except curses.error:
        cursor = True
        pass  # Terminal doesn't support hiding the cursor

    frames = [lines[i : i + LPF] for i in range(0, len(lines), LPF)]

    previous_frame = [" " * COLUMNS for _ in range(LPF - 1)]  # Exclude timestamp line

    for frame in frames:
        frame_time = int(frame[0])
        content_lines = frame[1:]

        for y, line in enumerate(content_lines):
            line = line.rstrip("\n").ljust(COLUMNS)
            prev_line = previous_frame[y]

            if line != prev_line:
                for x, (new_char, old_char) in enumerate(zip(line, prev_line)):
                    if new_char != old_char:
                        window.addch(y + 1, x + 1, new_char.encode("ascii"))  # +1 for 1-based coord

            previous_frame[y] = line  # Update previous frame

        window.refresh()
        if cursor:
            window.move(1, 24)
        time.sleep(frame_time * 0.06)  # frametime * 1/15 seconds


def run() -> None:
    """Start main with curses wrapper."""
    os.system("clear")

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    run()
