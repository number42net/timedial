import logging
import subprocess
from typing import TYPE_CHECKING

from timedial.accounts import account
from timedial.interface.menu_data import MainMenu, MenuItem

logger = logging.getLogger("Test")


def Config() -> MainMenu:
    login_user = subprocess.check_output(["whoami"]).decode().strip()
    user = account.read(login_user)
    items = []

    for name, field in account.UserModel.model_fields.items():
        extra = field.json_schema_extra
        if isinstance(extra, dict) and not extra.get("menu_visible", True):
            continue

        # value = getattr(user, name)
        items.append(
            MenuItem(
                name=field.title if field.title else name,
                description=field.description if field.description else "",
                callable="Test",
            )
        )

    return MainMenu(**{"items": items})
