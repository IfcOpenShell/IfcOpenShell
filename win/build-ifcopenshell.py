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
import multiprocessing
import os
import sys
from typing import NamedTuple, NoReturn

from common import (
    BUILD_CFG_DEFAULT,
    BUILD_CFGS,
    PROJECT_NAME,
    REPO_ROOT,
    BuildCfg,
    C,
    HelpStrings,
    colorize,
    ensure_script_dir,
    logger,
    resolve_generator,
    run_streamed,
)
from vs_cfg import vs_cfg


class Args(NamedTuple):
    generator: str | None
    build_cfg: BuildCfg
    num_build_procs: int
    target: str | None
    extra_args: list[str]


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # TODO: this hint can be removed later, it's just for anyone transitioning from build-ifcopenshell.bat,
        # which allowed providing additional args as positionals. We disallow it here (they can be passed after
        # '--') to ensure we can validate the provided args.
        if message.startswith("unrecognized arguments"):
            message += (
                "\nHint: put args meant for the underlying build tool (e.g. MSBuild) after '--', "
                "e.g. `build-ifcopenshell.py -- /p:Foo=bar`."
            )
        super().error(message)


def parse_args() -> Args:
    parser = ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Arguments after '--' are passed through as-is to the underlying build tool (e.g. MSBuild).",
    )
    parser.add_argument(
        "generator",
        nargs="?",
        default=None,
        help=HelpStrings.generator("GEN_SHORTHAND from the most recently modified BuildDepsCache-*.txt is used"),
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
    parser.add_argument(
        "--num-build-procs",
        dest="num_build_procs",
        type=int,
        default=argparse.SUPPRESS,
        help=HelpStrings.NUM_BUILD_PROCS,
    )
    parser.add_argument(
        "--target",
        dest="target",
        default=None,
        help=(
            "cmake --build target, passed as-is. E.g. 'INSTALL' to also install after building. "
            "By default no target is passed, which builds the whole solution."
        ),
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

    num_build_procs = getattr(args, "num_build_procs", None) or int(
        os.getenv("IFCOS_NUM_BUILD_PROCS") or multiprocessing.cpu_count()
    )

    return Args(
        generator=generator,
        build_cfg=build_cfg,
        num_build_procs=num_build_procs,
        target=args.target,
        extra_args=extra_args,
    )


def main() -> None:
    ARGS = parse_args()

    ensure_script_dir()

    generator = resolve_generator(ARGS.generator)

    vs_cfg_vars = vs_cfg(generator, REPO_ROOT)

    logger.info("")
    logger.info(colorize(f"* IFCOS_NUM_BUILD_PROCS\t= {ARGS.num_build_procs}", C.PURPLE))
    logger.info("")

    if ARGS.target:
        target_suffix = f" (target: {ARGS.target})"
        target_args = ("--target", ARGS.target)
    else:
        target_suffix = ""
        target_args = ()
    logger.info(
        colorize(f"Building {vs_cfg_vars.vs_platform} {ARGS.build_cfg} {PROJECT_NAME}{target_suffix}", C.PURPLE)
    )
    MSBUILD_MULTIPROC = (
        "/m",
        f"/p:CL_MPCount={ARGS.num_build_procs}",
        "/p:UseMultiToolTask=true",
        "/p:EnforceProcessCountAcrossBuilds=true",
    )
    run_streamed(
        "cmake",
        "--build",
        str(REPO_ROOT / vs_cfg_vars.build_dir),
        *target_args,
        "--",
        "/nologo",
        *MSBUILD_MULTIPROC,
        f"/p:Platform={vs_cfg_vars.vs_platform}",
        f"/p:Configuration={ARGS.build_cfg}",
        *ARGS.extra_args,
    )

    logger.info("")
    logger.info(colorize(f"{vs_cfg_vars.vs_platform} {ARGS.build_cfg} {PROJECT_NAME} build finished.", C.GREEN))


if __name__ == "__main__":
    main()
