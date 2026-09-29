# /// script
# ///

# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""
Add the Bonsai unstable extensions repository to Blender, install Bonsai from it and enable it
(unless another instance of Bonsai is already enabled).

Note: enables "Allow Online Access" in Blender preferences.

CLI Usage: blender --background --python install-bonsai-unstable.py

From Blender: copy and paste the entire script into Blender's Scripting tab text editor and run it.
Logs are printed to the system console (Window > Toggle System Console on Windows).
"""

import logging
import tomllib
from pathlib import Path

import bpy


class C:
    GREY = "\033[90m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: C.GREY,
        logging.WARNING: C.YELLOW,
        logging.ERROR: C.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, C.RESET)
        return f"{color}{super().format(record)}{C.RESET}"


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(name)s: %(message)s"))
logger = logging.getLogger("install-bonsai-unstable")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

REPO_URL = "https://raw.githubusercontent.com/IfcOpenShell/bonsai_unstable_repo/main/index.json"


def main() -> None:
    preferences = bpy.context.preferences
    assert preferences
    preferences.system.use_online_access = True
    repos = preferences.extensions.repos
    repo = next((r for r in repos if r.remote_url == REPO_URL), None)
    if repo:
        logger.info("Repository '%s' already exists.", repo.name)
    else:
        repo = repos.new(name="Bonsai Unstable", module="bonsai_unstable", remote_url=REPO_URL)
        logger.info("Added repository '%s'.", repo.name)

    repo.enabled = True
    repo.use_remote_url = True
    repo.use_sync_on_startup = True

    repo_index = list(repos).index(repo)
    bpy.ops.extensions.repo_sync(repo_index=repo_index)
    addon_module = f"bl_ext.{repo.module}.bonsai"
    enabled_elsewhere = [r.name for r in repos if r != repo and f"bl_ext.{r.module}.bonsai" in preferences.addons]
    package_dir = Path(repo.directory) / "bonsai"
    if package_dir.is_dir():
        logger.info("Unstable Bonsai is already installed.")
        if addon_module in preferences.addons:
            logger.info("Unstable Bonsai is already enabled.")
        elif not enabled_elsewhere:
            bpy.ops.preferences.addon_enable(module=addon_module)
            logger.info("Enabled Unstable Bonsai.")
    else:
        bpy.ops.extensions.package_install(
            repo_index=repo_index, pkg_id="bonsai", enable_on_install=not enabled_elsewhere
        )
    manifest = tomllib.loads((package_dir / "blender_manifest.toml").read_text())
    logger.info("Unstable Bonsai version: %s.", manifest["version"])
    if enabled_elsewhere and addon_module not in preferences.addons:
        logger.warning(
            "Bonsai is already enabled from %s. Unstable Bonsai is left disabled, "
            "disable the other Bonsai before enabling it.",
            ", ".join(enabled_elsewhere),
        )
    bpy.ops.wm.save_userpref()


if __name__ == "__main__":
    main()
