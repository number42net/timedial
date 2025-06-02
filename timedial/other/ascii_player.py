"""ASCII player, based on https://github.com/mgracanin/ASCIIStarWars.

ASCII Art (Star Wars) from https://www.asciimation.co.nz/
"""

import asyncio
import os
import sys
from asyncio import sleep

starwars_file_path = "/opt/demos/starwars.txt"
os.system("clear")
LPS = 14  ## Lines per frame


async def main() -> None:
    """Main player."""
    try:
        with open(starwars_file_path) as f:
            podaci = f.read().split("\n")
        print("\n" * LPS)
    except FileNotFoundError:
        print(f"File {starwars_file_path} does not exist. \nMake sure file is in the same directory as this script and try again.")
        sys.exit(1)

    ## Each frame is 67 columns by 14 rows, so interating the file in chunks of LPS lines
    for i in range(0, len(podaci), LPS):
        print("\x1b[{}A\x1b[J{}".format(LPS, "\n".join(podaci[i + 1 : i + LPS])))  # \x1b[{}A\x1b[J move ESC char 14 lines
        await sleep(int(podaci[i]) * 67 / 1000)  ## Delay = 67


def run() -> None:
    """Start the main player as asyncio."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    run()
