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

import subprocess

from timedial.accounts import account


def main() -> None:
    """Greet the currently logged-in user."""
    try:
        login_user = subprocess.check_output(["logname"]).decode().strip()
        user = account.read(login_user)

    except Exception:
        exit(1)

    name = user.realname if user.realname else user.username
    print(f"Welcome to TimeDial.org {name}!")
