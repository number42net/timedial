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
# Work in progress, will get back to this

# import logging
# import subprocess
# from typing import TYPE_CHECKING

# from timedial.accounts import account
# from timedial.interface.menu_data import MainMenu, MenuItem

# logger = logging.getLogger("Test")


# def Config() -> MainMenu:
#     """Generates the main configuration menu for the current user.

#     This function retrieves the currently logged-in user's username,
#     loads their account information, and constructs a list of menu
#     items based on the fields in the user model that are marked as
#     visible in the menu.

#     Returns:
#         MainMenu: An instance of MainMenu containing the constructed menu items.
#     """
#     login_user = subprocess.check_output(["whoami"]).decode().strip()
#     user = account.read(login_user)
#     items = []

#     for name, field in account.UserModel.model_fields.items():
#         extra = field.json_schema_extra
#         if isinstance(extra, dict) and not extra.get("menu_visible", True):
#             continue

#         # value = getattr(user, name)
#         items.append(
#             MenuItem(
#                 name=field.title if field.title else name,
#                 description=field.description if field.description else "",
#                 callable="Test",
#             )
#         )

#     return MainMenu(**{"items": items})
