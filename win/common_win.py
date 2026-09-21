###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################
#
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from common import SCRIPT_DIR, logger

if TYPE_CHECKING:
    from vs_cfg import VsCfgResult


class BuildDepsCache:
    def __init__(self, vs_cfg_vars: VsCfgResult) -> None:
        if vs_cfg_vars.vs_toolset_override:
            self.path = SCRIPT_DIR / f"BuildDepsCache-{vs_cfg_vars.vs_platform}-{vs_cfg_vars.vs_toolset_override}.txt"
        else:
            self.path = SCRIPT_DIR / f"BuildDepsCache-{vs_cfg_vars.vs_platform}.txt"
        self.path.write_text("")

    def add_entry(self, key: str, value: str) -> None:
        with self.path.open("a") as f:
            f.write(f"{key}={value}\n")

    @staticmethod
    def parse(path: Path) -> dict[str, str]:
        entries: dict[str, str] = {}
        for line in path.read_text().splitlines():
            key, _, value = line.partition("=")
            entries[key] = value
        return entries


def msbuild_multiproc_args(num_build_procs: int) -> tuple[str, ...]:
    return (
        "/m",
        f"/p:CL_MPCount={num_build_procs}",
        "/p:UseMultiToolTask=true",
        "/p:EnforceProcessCountAcrossBuilds=true",
    )


def resolve_generator(generator: str | None) -> str:
    """Return `generator` as-is, or fall back to the GEN_SHORTHAND from the most recently modified
    BuildDepsCache-*.txt. Exits if neither is available.
    """
    if generator is not None:
        return generator

    cache_files = sorted(SCRIPT_DIR.glob("BuildDepsCache-*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    cached_generator = None
    if cache_files:
        cache_file = cache_files[0]
        logger.info(f"Found {cache_file.name}, reading GEN_SHORTHAND from it.")
        cached_generator = BuildDepsCache.parse(cache_file).get("GEN_SHORTHAND")

    if cached_generator is None:
        logger.error(
            "BuildDepsCache file does not exist and/or GEN_SHORTHAND missing from it. Run build-deps.py to create it."
        )
        sys.exit(1)
    return cached_generator
