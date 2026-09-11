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

import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal, get_args

if TYPE_CHECKING:
    from vs_cfg import VsCfgResult


class C:
    GREY = "\033[90m"
    GREEN = "\033[92m"
    PURPLE = "\033[95m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}"


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
handler.setFormatter(ColorFormatter("%(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger()

SCRIPT_DIR = Path(__file__).resolve().parent
# TODO: used to access nix patch.
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_NAME = "IfcOpenShell"


def run(
    *cmd: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> str:
    logger.debug(f"$ {shlex.join(cmd)}")
    return subprocess.check_output(cmd, cwd=cwd, env=env, text=True)


def run_streamed(
    *cmd: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> None:
    logger.info(f"$ {shlex.join(cmd)}")
    full_env = {**os.environ, **env} if env is not None else None
    subprocess.check_call(cmd, cwd=cwd, env=full_env)


def is_on_off(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    lowered = value.lower()
    if lowered in {"1", "on", "true", "yes"}:
        return True
    if lowered in {"0", "off", "false", "no"}:
        return False
    return default


OFF_ON = ("OFF", "ON")


BuildCfg = Literal["MinSizeRel", "Release", "RelWithDebInfo", "Debug"]
DebugOrRelease = Literal["Debug", "Release"]

BUILD_CFGS = get_args(BuildCfg)
BUILD_CFG_DEFAULT: BuildCfg = "RelWithDebInfo"

BuildType = Literal["Build", "Rebuild", "Clean"]

BUILD_TYPES = get_args(BuildType)
BUILD_TYPE_DEFAULT: BuildType = "Build"


class HelpStrings:
    NUM_BUILD_PROCS = (
        "How many build processes may be run in parallel. "
        "Also can be specified by using IFCOS_NUM_BUILD_PROCS env variable. "
        "(default: NUMBER_OF_PROCESSORS)"
    )

    GENERATOR_FLAG = (
        "Alternative way to specify the generator, instead of the positional argument. See above for accepted forms."
    )

    BUILD_CFG = f"Build configuration type. (default: {BUILD_CFG_DEFAULT})"
    BUILD_CFG_FLAG = "Alternative way to specify the build configuration type, instead of the positional argument."

    @staticmethod
    def generator(omitted_behavior: str) -> str:
        return (
            "CMake generator to use. Accepts 3 forms: "
            f"(1) omitted - {omitted_behavior}; "
            "(2) shorthand, e.g. 'vs2022', 'vs2022-x64', 'vs2019-x86-v141' - optionally provide platform/toolset "
            "using the suffix; "
            "(3) full CMake generator name, e.g. 'Visual Studio 17 2022'."
        )


def debug_or_release(build_cfg: BuildCfg) -> DebugOrRelease:
    return "Debug" if build_cfg == "Debug" else "Release"


def ensure_script_dir() -> None:
    if Path.cwd() != SCRIPT_DIR:
        logger.error(f"This script must be run from '{SCRIPT_DIR}'.")
        sys.exit(1)


def require_command(command: str) -> str:
    path = shutil.which(command)
    if not path:
        logger.error(f"Required tool '{command}' not installed or not added to PATH.")
        sys.exit(1)
    return path


def validate_cmake_version() -> None:
    MIN_CMAKE_VERSION = (3, 21, 0)
    error_msg = f"CMake v{'.'.join(map(str, MIN_CMAKE_VERSION))} or higher is required"

    if not shutil.which("cmake"):
        logger.error(error_msg)
        sys.exit(1)

    cmake_version_output = run("cmake", "--version")
    match = re.search(r"cmake version (\d+)\.(\d+)\.(\d+)", cmake_version_output)
    if not match or tuple(map(int, match.groups())) < MIN_CMAKE_VERSION:
        logger.error(error_msg)
        sys.exit(1)


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
