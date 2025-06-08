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

import gzip
import logging
import os
import shutil
import time
from datetime import datetime

from timedial.config import config
from timedial.logger import daemon_logger_config

daemon_logger_config()
logger = logging.getLogger("timedial.stale_files")


def compress_stale() -> None:
    """Recursively scan HOME_DIR and gzip stale, large, uncompressed files."""
    age_limit: float = time.time() - (config.stale_files_age)
    for dirpath, _, filenames in os.walk("/home"):
        for fname in filenames:
            path: str = os.path.join(dirpath, fname)
            try:
                if not os.path.isfile(path):
                    continue
                if os.path.getsize(path) < config.stale_files_size:
                    continue
                if os.path.getatime(path) > age_limit or os.path.getmtime(path) > age_limit:
                    continue
                with open(path, "rb") as f_in:
                    if f_in.read(2) == b"\x1f\x8b":
                        continue
                    with gzip.open(path + ".gz", "wb") as f_out:
                        f_in.seek(0)
                        shutil.copyfileobj(f_in, f_out)
                os.remove(path)
                logger.info(f"Compressed: {path}")

            except Exception as exc:
                logger.exception(f"Error processing {path}: {exc}")


def main() -> None:
    """Continuously run the scanner every SLEEP_INTERVAL_SECONDS."""
    while True:
        logger.info(f"[{datetime.now()}] Starting scan...")
        compress_stale()
        logger.info(f"[{datetime.now()}] Scan complete. Sleeping for {config.stale_files_sleep} seconds.")
        time.sleep(config.stale_files_sleep)


if __name__ == "__main__":
    main()
