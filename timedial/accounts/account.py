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
import grp
import os
import pwd
import re
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from timedial.config import config

USERNAME_REGEX = re.compile(r"^[a-z0-9]+$")


def validate_username(username: str) -> bool:
    """Check whether a username matches the allowed pattern.

    Args:
        username (str): The username to validate.

    Returns:
        bool: True if valid, False otherwise.

    """
    return bool(USERNAME_REGEX.fullmatch(username))


def read(username: str = getpass.getuser()) -> "UserModel":
    """Read and parse a UserModel from the JSON file associated with the given username.

    Args:
        username (str): The username to look up.

    Returns:
        UserModel: The parsed user model.

    Raises:
        ValueError: If the username is invalid.
        FileNotFoundError: If the user's file does not exist.

    """
    if not validate_username(username):
        raise ValueError("Invalid username")

    with open(os.path.join(config.guest_dir, f"{username}.json")) as f:
        json_data = f.read()

    return UserModel.model_validate_json(json_data)


def user_exists(username: str) -> bool:
    """Check if json file exists for a given user.

    Args:
        username (str): The username to look up.

    Returns:
        bool

    """
    return os.path.isfile(os.path.join(config.guest_dir, f"{username}.json"))


def availble_ids(start: int = 1000, max_id: int = 60000) -> tuple[int, int]:
    """Find the next available UID and GID that are equal in value and unused.

    This function ensures the returned UID and GID are the same number,
    and that number is unused by any existing user or group on the system.

    Args:
        start (int, optional): The minimum UID/GID to consider. Defaults to 1000.
        max_id (int, optional): The maximum UID/GID to check. Defaults to 60000.

    Returns:
        tuple: A tuple (uid_gid, uid_gid) where the UID and GID are equal.

    Raises:
        ValueError: If no matching UID/GID pair is found in the specified range.
    """
    used_uids = {user.pw_uid for user in pwd.getpwall() if user.pw_uid >= start}
    used_gids = {group.gr_gid for group in grp.getgrall() if group.gr_gid >= start}

    for id_val in range(start, max_id):
        if id_val not in used_uids and id_val not in used_gids:
            return id_val, id_val

    raise ValueError("No matching UID and GID found in the specified range.")


class UserModel(BaseModel):
    """Pydantic model representing a user with optional fields and validation.

    Attributes:
        username (str): A unique, immutable username (lowercase letters and digits only).
        password_hash (str): Hashed password string.
        email (str | None): Optional email address.
        pubkeys (list[str] | None): Optional list of public keys.
        realname (str | None): Optional real name of the user.
        _path (str): Internal path for storing this user's JSON data (private attribute).

    """

    id: tuple[int, int] = Field(
        frozen=True,
        title="User ID",
        description="A unique, immutable POSIX user and group ID.",
        json_schema_extra={"menu_visible": False},
        default=availble_ids(),
    )

    username: str = Field(
        ...,
        frozen=True,
        title="Username",
        description="A unique, immutable username (lowercase letters and digits only).",
        json_schema_extra={"menu_visible": False},
    )
    password_hash: str = Field(
        ...,
        title="Password",
        description="Hashed password string.",
    )
    email: str | None = Field(
        default=None,
        title="Email Address",
        description="Optional email address.",
    )
    pubkeys: list[str] = Field(
        default_factory=list,
        title="Public Keys",
        description="Optional list of public keys.",
    )
    realname: str | None = Field(
        default=None,
        title="Real Name",
        description="Optional real name of the user.",
    )
    lastlogin: float = Field(
        default_factory=time.time,
        title="Last Login Timestamp",
        description="Timestamp of the user's last login (epoch seconds).",
        json_schema_extra={"menu_visible": False},
    )
    _yaml_path: str = PrivateAttr()

    model_config = ConfigDict(
        extra="forbid",
    )

    def model_post_init(self, __context: Any) -> None:
        """Compute the path where the user's data is stored after model initialization."""
        self._yaml_path = os.path.join(config.guest_dir, f"{self.username}.json")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Validate that the username contains only lowercase letters and digits.

        Args:
            value (str): The username to validate.

        Returns:
            str: The validated username.

        Raises:
            ValueError: If the username does not match the expected pattern.

        """
        if not validate_username(value):
            raise ValueError("Username must contain only lowercase letters and digits.")
        return value

    def config_fields(self) -> dict[str, Any]:
        """Return user-editable fields only (excluding system-managed fields)."""
        return {name: field for name, field in UserModel.model_fields.items() if name not in {"lastlogin"}}

    def write(self) -> None:
        """Write the given UserModel to its corresponding JSON file."""
        with open(self._yaml_path, "w") as f:
            f.write(self.model_dump_json(indent=4))

    def new_login(self) -> None:
        """Reset the last login time and write the data."""
        self.lastlogin = time.time()
        self.write()
