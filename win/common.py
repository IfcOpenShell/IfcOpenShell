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
from typing import Any, Literal, TypeVar, cast, get_args


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


T = TypeVar("T")


def resolve_cli_or_env(
    cli_value: T | None, env_var_name: str, default: T, *, arg_type: Literal["str", "int", "bool"]
) -> T:
    if cli_value is not None:
        return cli_value
    env_value = os.getenv(env_var_name)
    if not env_value:
        return default
    logger.info(f"Using {env_var_name} from env: '{env_value}'")
    parsed: Any = env_value
    if arg_type == "str":
        parsed = env_value
    elif arg_type == "int":
        parsed = int(env_value)
    elif arg_type == "bool":
        parsed = is_on_off(env_value, default=True)
    else:
        # TODO: use assert_never once we bump min version to 3.11.
        assert False, f"Unhandled arg_type: {arg_type!r}"
    return cast(T, parsed)


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
