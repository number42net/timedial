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

#!/usr/bin/env python3
import crypt
import os
import sys

from timedial.accounts import account
from timedial.logger import get_logger

logger = get_logger("pam")


def pam_module() -> None:
    """Entry point for the PAM module.

    Initializes a GuestDB instance, which performs either authentication
    or account checks based on the PAM_TYPE environment variable.

    Exits with code 1 in case of an unhandled exception.
    """
    try:
        GuestDB()
    except Exception as exc:
        logger.error(f"Unhandled exception {exc}")
        sys.exit(1)


class GuestDB:
    """PAM integration class for guest account authentication and access control.

    Upon instantiation, determines the current PAM operation type
    (authentication or account validation) and calls the appropriate method.

    Attributes:
        username (str): The PAM username obtained from the environment.
        account (timedial.accounts.account.Account): The corresponding account object.

    """

    def __init__(self) -> None:
        """Initialize the GuestDB instance."""
        self.username = os.environ.get("PAM_USER", "")
        if not self.username:
            logger.error("No username received")
            sys.exit(1)

        if not account.user_exists(self.username):
            logger.error(f"User: {self.username} doesn't exist")
            sys.exit(1)

        try:
            self.user_account = account.read(self.username)
        except Exception as e:
            logger.error(f"Error reading user file {e}", exc_info=True)
            sys.exit(1)

        pam_type = os.environ.get("PAM_TYPE", "")
        if pam_type == "auth":
            self.auth()
        elif pam_type == "account":
            self.account()

    def auth(self) -> None:
        """Handle PAM authentication requests.

        Reads the password from stdin or the PAM_AUTHTOK environment variable.
        Validates the password using crypt against the stored password hash.

        Exits with code 0 if authentication is successful,
        or code 1 if it fails due to missing or incorrect credentials.
        """
        password = sys.stdin.read()
        if not password:
            password = os.environ.get("PAM_AUTHTOK", "")
        if not password:
            logger.error("No password supplied")
            sys.exit(1)

        new_hash = crypt.crypt(password, self.user_account.password_hash)
        if new_hash != self.user_account.password_hash:
            logger.error("Invalid password!")
            sys.exit(1)

        # Success
        logger.info(f"Passed PAM auth request for: {self.username}")
        sys.exit(0)

    def account(self) -> None:
        """Handle PAM account validation requests.

        Logs success and exits with code 0.
        """
        logger.info(f"Passed PAM account request for: {self.username}")
        sys.exit(0)
