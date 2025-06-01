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

import logging
import os

import tomllib

from timedial.config import config
from timedial.interface.menu_data import Command, MainMenu, MenuItem
from timedial.logger import ui_logger_config
from timedial.other.start_sim import ConfigModel

ui_logger_config()
logger = logging.getLogger("timedial.simmenu")


def load_simulators() -> MainMenu:
    """Loads available simulators from global and local directories.

    This function searches for simulator configurations in two locations:
    a global simulator directory defined in the application config, and a
    local simulator directory under the user's home directory (`~/simulators`).

    Each simulator must contain a `simulator.toml` file which is parsed into
    a `ConfigModel`. The information is used to construct `MenuItem` entries,
    which are added to the main menu.

    Returns:
        MainMenu: A menu object containing all the discovered simulators,
        sorted alphabetically by name.
    """
    simulators: list[MenuItem] = []
    home_dir = os.path.expanduser("~/simulators")
    global_sims = os.listdir(config.simulator_path)
    if os.path.isdir(home_dir):
        local_sims = os.listdir(home_dir)
        logger.debug(local_sims)
    else:
        logger.debug("No local sims...")
        local_sims = []

    global_sims.sort()
    local_sims.sort()

    all_sims = {sim: os.path.join(config.simulator_path, sim) for sim in global_sims}

    logger.debug(all_sims)
    all_sims.update({sim: os.path.join(home_dir, sim) for sim in local_sims})
    logger.debug(all_sims)

    for name, path in all_sims.items():
        config_file = os.path.join(path, "simulator.toml")
        if not os.path.isdir(path):
            continue
        if not os.path.isfile(config_file):
            continue

        try:
            with open(config_file, "rb") as f:
                data = ConfigModel(**tomllib.load(f))
        except Exception as exc:
            logger.exception(f"Failed load {config_file}: {exc}")

        if isinstance(data.description.text, str):
            data.description.text = [data.description.text]

        simulators.append(
            MenuItem(
                name=data.emulator.label,
                description=data.description.text,
                command=Command(
                    exec=["/usr/local/bin/timedial-start-sim", name],
                    version=data.description.version,
                    publisher=data.description.publisher,
                    original_date=data.description.original_date,
                    version_date=data.description.version_date,
                ),
            )
        )
        logger.debug(simulators[-1])

    return MainMenu(items=sorted(simulators, key=lambda x: x.name))


if __name__ == "__main__":
    load_simulators()
