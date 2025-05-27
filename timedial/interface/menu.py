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

from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_validator, model_validator
from ruamel.yaml import YAML

MENU_FILE = "/opt/timedial/menu.yaml"

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

    publisher: str
    original_date: str
    version: str
    version_date: str
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
    """Represents a menu item in the hierarchical menu system.

    A MenuItem must either contain a list of sub-items (items) or a command to execute,
    but not both.

    Attributes:
        id: Unique identifier for the menu item.
        name: Human-readable name.
        command: Command to execute if this is a leaf item.
        items: List of child MenuItems if this is a group node.
    """

    id: str
    name: str
    command: Command | None = None
    items: list["MenuItem"] | None = None

    @model_validator(mode="after")
    def check_command_or_items(self) -> Self:
        """Validates that a MenuItem has either 'command' or 'items', but not both or neither."""
        if (not self.command and not self.items) or (self.command and self.items):
            raise ValueError("Each MenuItem must have either a command or items.")
        return self


MenuItem.model_rebuild()


def load_menu() -> MenuItem:
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

    return MenuItem(**data["mainmenu"])
