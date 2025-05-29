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

import argparse
import logging
import sys

from timedial.accounts import account
from timedial.logger import auth_logger_config

auth_logger_config()
logger = logging.getLogger("timedial.pubkeys")

parser = argparse.ArgumentParser(description="Script that takes a username as a positional argument.")

# Add the positional username argument
parser.add_argument("username", type=str, help="Your username")

# Parse the arguments
args = parser.parse_args()


def main() -> None:
    if not args.username:
        logger.error("No username received")
        sys.exit(1)

    if args.username == "guest":
        # No pub keys allowed for guest
        sys.exit(0)

    if not account.user_exists(args.username):
        logger.error(f"User: {args.username} doesn't exist in guest DB, checking filesystem")
        sys.exit(1)
        # fs(args.username)

    try:
        user_account = account.read(args.username)
    except Exception as e:
        logger.error(f"Error reading user file {e}", exc_info=True)
        sys.exit(1)

    for key in user_account.pubkeys:
        print(key)
