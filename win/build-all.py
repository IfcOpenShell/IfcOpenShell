# /// script
# [tool.ty.environment]
# root = ["."]
# ///
###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                        #
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
import argparse
import subprocess
import sys
from typing import NamedTuple, NoReturn

from common import (
    BUILD_CFG_DEFAULT,
    BUILD_CFGS,
    SCRIPT_DIR,
    BuildCfg,
    HelpStrings,
    ensure_script_dir,
    logger,
    run_streamed,
)


class Args(NamedTuple):
    generator: str | None
    build_cfg: BuildCfg
    extra_args: list[str]


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # TODO: same as in build-ifcopenshell.py/run-cmake.py, can be removed later.
        if message.startswith("unrecognized arguments"):
            message += (
                "\nHint: put args meant for CMake after '--', e.g. `build-all.py vs2022-x64 -- -DGLTF_SUPPORT=ON`."
            )
        super().error(message)


def parse_args() -> Args:
    parser = ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Arguments after '--' are passed through as-is to CMake, e.g. -DGLTF_SUPPORT=ON.",
    )
    parser.add_argument(
        "generator",
        nargs="?",
        default=None,
        help=HelpStrings.generator("deduced from the active Visual Studio environment"),
    )
    parser.add_argument(
        "--generator",
        dest="generator_flag",
        default=None,
        help=HelpStrings.GENERATOR_FLAG,
    )
    parser.add_argument(
        "build_cfg",
        nargs="?",
        default=argparse.SUPPRESS,
        choices=BUILD_CFGS,
        help=HelpStrings.BUILD_CFG,
    )
    parser.add_argument(
        "--build-cfg",
        dest="build_cfg_flag",
        default=BUILD_CFG_DEFAULT,
        choices=BUILD_CFGS,
        help=HelpStrings.BUILD_CFG_FLAG,
    )
    argv = sys.argv[1:]
    if "--" in argv:
        separator_idx = argv.index("--")
        own_argv, extra_args = argv[:separator_idx], argv[separator_idx + 1 :]
    else:
        own_argv, extra_args = argv, []

    args = parser.parse_args(own_argv)

    if args.generator is not None and args.generator_flag is not None:
        parser.error("generator was specified both as a positional argument and as --generator.")
    generator = args.generator or args.generator_flag

    build_cfg = getattr(args, "build_cfg", None) or args.build_cfg_flag

    return Args(generator=generator, build_cfg=build_cfg, extra_args=extra_args)


def main() -> None:
    ARGS = parse_args()

    ensure_script_dir()

    generator_args = [ARGS.generator] if ARGS.generator else []

    # Auto-answer build-deps.py's "are you ready" prompt, same trick as build-all.cmd's "echo y |".
    build_deps_cmd = [sys.executable, str(SCRIPT_DIR / "build-deps.py"), *generator_args, ARGS.build_cfg]
    logger.info(f"$ {' '.join(build_deps_cmd)}")
    subprocess.run(build_deps_cmd, input="y\n", text=True, check=True)

    run_streamed(sys.executable, str(SCRIPT_DIR / "run-cmake.py"), *generator_args, "--", *ARGS.extra_args)
    run_streamed(sys.executable, str(SCRIPT_DIR / "build-ifcopenshell.py"), *generator_args, ARGS.build_cfg)
    run_streamed(sys.executable, str(SCRIPT_DIR / "install-ifcopenshell.py"), *generator_args, ARGS.build_cfg)


if __name__ == "__main__":
    main()
