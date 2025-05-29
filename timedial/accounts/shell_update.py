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

import getpass
import subprocess

import bcrypt

from timedial.accounts import account

login_user = subprocess.check_output(["whoami"]).decode().strip()
user = account.read(login_user)


def main() -> None:
    """Interactive CLI for updating user account information.

    Prompts the logged-in user to review and optionally update each field in their account,
    including securely changing the password if desired. Updates are saved only if changes
    are made.

    Fields marked with 'menu_visible: false' in their metadata are skipped.
    """
    change = False
    for name, field in account.UserModel.model_fields.items():
        extra = field.json_schema_extra
        if isinstance(extra, dict) and not extra.get("menu_visible", True):
            continue

        title = field.title if field.title else name
        value = getattr(user, name)
        if isinstance(value, list):
            value = ",".join(value)

        if name == "password_hash":
            while True:
                pass1 = getpass.getpass(f"{title} [Blank to skip change]: ")
                if not pass1:
                    break
                pass2 = getpass.getpass(f"{title} [Repeat]: ")

                if not pass1 == pass2:
                    print("Passwords do not match")
                    continue

                hashed = bcrypt.hashpw(pass1.encode("utf-8"), bcrypt.gensalt())
                user.password_hash = hashed.decode("utf-8")
                change = True
                break
        else:
            update: str | list[str] = input(f"{title} [{value}]: ").strip()
            if update:
                change = True
                if isinstance(getattr(user, name), list) and isinstance(update, str):
                    update = [i.strip() for i in update.split(",")]
                setattr(user, name, update)

    if change:
        user.write()
        print("Information updated!")
    else:
        print("Nothing changed")

    print("\nPress enter to continue...")
    input()


if __name__ == "__main__":
    main()
