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

from pathlib import Path

from pydantic import BaseModel, field_validator
from ruamel.yaml import YAML

MENU_FILE = "/opt/timedial//menu.yaml"
# MENU_FILE = "files/menu.yaml"

yaml = YAML()


class Command(BaseModel):
    """Represents a shell or program command definition.

    Attributes:
        publisher: Name of the organization or person that released the command.
        original_date: Year or date the command was originally released.
        version: Version identifier for the command.
        version_date: Date this version was released.
        exec: List of strings representing the executable and arguments.
    """

    publisher: str | None = None
    original_date: str | None = None
    version: str | None = None
    version_date: str | None = None
    exec: list[str]

    @field_validator("exec")
    @classmethod
    def validate_exec(cls, v: list[str]) -> list[str]:
        """Validates the 'exec' field.

        Ensures it contains at least one non-empty string and that the first string
        is an absolute path.
        """
        if not v:
            raise ValueError("exec must contain at least one command")

        if any(s.strip() == "" for s in v):
            raise ValueError("exec cannot contain empty strings")

        first_path = Path(v[0])
        if not first_path.is_absolute():
            raise ValueError("The first exec value must be an absolute path")

        return v


class MenuItem(BaseModel):
    name: str
    description: str | list[str]
    items: list["MenuItem"] | None = None
    command: Command | None = None
    callable: str | None = None


class MainMenu(BaseModel):
    items: list[MenuItem]


def load_menu() -> MainMenu:
    """Loads the menu configuration from disk and validates it.

    Returns:
        A fully validated MenuItem instance representing the root menu.

    Raises:
        RuntimeError: If the menu file is missing or cannot be parsed.
        ValueError: If required fields are missing or invalid in the YAML data.
    """
    try:
        with open(MENU_FILE) as file:
            data = yaml.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Menu file not found: {MENU_FILE}") from exc
    except KeyError as exc:
        raise ValueError("Missing 'mainmenu' key in YAML file.") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to load menu: {exc}") from exc

    return MainMenu(items=data["mainmenu"])
