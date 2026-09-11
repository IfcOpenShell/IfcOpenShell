# /// script
# [tool.ty.environment]
# # Lets ty resolve sibling imports (common, installers, etc).
# root = ["."]
# ///
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
import argparse
import multiprocessing
import os
import shutil
import sys
from datetime import datetime
from typing import NamedTuple

from common import (
    BUILD_CFG_DEFAULT,
    BUILD_CFGS,
    BUILD_TYPE_DEFAULT,
    BUILD_TYPES,
    PROJECT_NAME,
    REPO_ROOT,
    SCRIPT_DIR,
    BuildCfg,
    BuildDepsCache,
    BuildType,
    C,
    HelpStrings,
    colorize,
    ensure_script_dir,
    is_on_off,
    logger,
    require_command,
    validate_cmake_version,
)
from installers import (
    install_boost,
    install_ccache,
    install_cgal,
    install_eigen,
    install_json,
    install_manifold,
    install_mpfr,
    install_mpir,
    install_nuget,
    install_occt,
    install_opencollada,
    install_proj,
    install_python,
    install_qt6,
    install_rocksdb,
    install_swig,
    install_zstd,
)
from vs_cfg import VsCfgResult, get_vs_var, vs_cfg


class Args(NamedTuple):
    generator: str | None
    build_cfg: BuildCfg
    build_type: BuildType
    reuse_boost: bool
    num_build_procs: int
    install_python: bool
    install_qt6: bool


def print_build_config(
    vs_cfg_vars: VsCfgResult,
    build_cfg: BuildCfg,
    build_type: BuildType,
    ifcos_install_python: bool,
    ifcos_install_qt6: bool,
    ifcos_num_build_procs: int,
) -> None:
    def field(text: str) -> str:
        return colorize(text, C.PURPLE)

    logger.info(colorize("Script configuration:", C.GREEN))
    logger.info(field(f"* CMake Generator\t= '{vs_cfg_vars.generator.name}'"))
    logger.info("  - Passed to CMake -G option.")
    logger.info(field(f"* Target Platform\t= {vs_cfg_vars.vs_platform}"))
    logger.info("  - Whether were doing 32-bit (Win32) or 64-bit (x64, ARM64) build. Passed to CMake -A option.")
    logger.info(field(f"* Target Toolset Override\t= {vs_cfg_vars.vs_toolset_override}"))
    logger.info("  - Passed to CMake -T option.")
    logger.info(field(f"* Dependency Directory\t= {vs_cfg_vars.deps_dir}"))
    logger.info(f"  - The directory where {PROJECT_NAME} dependencies are fetched and built.")
    logger.info(field(f"* Installation Directory = {vs_cfg_vars.install_dir}"))
    logger.info(f"  - The directory where {PROJECT_NAME} dependencies are installed.")
    logger.info(field(f"* Build Config Type\t= {build_cfg}"))
    logger.info("  - The used build configuration type for the dependencies.")
    logger.info("    Defaults to RelWithDebInfo if not specified.")
    if build_cfg == "MinSizeRel":
        logger.warning("     WARNING: MinSizeRel build can suffer from a significant performance loss.")
    logger.info(field(f"* Build Type\t\t= {build_type}"))
    logger.info("  - The used build type for the dependencies (Build, Rebuild, Clean).")
    logger.info("    Defaults to Build if not specified.")
    logger.info(field(f"* IFCOS_INSTALL_PYTHON\t= {ifcos_install_python}"))
    logger.info("  - Download and install Python.")
    logger.info("    Set to something other than TRUE if you wish to use an already installed version of Python.")
    logger.info(
        "    But then you'll need to set PYTHONHOME env variable to your Python installation before running run-cmake.bat"
    )
    logger.info("    to your Python installation path.")
    logger.info(field(f"* IFCOS_INSTALL_QT6\t= {ifcos_install_qt6}"))
    logger.info("  - Download and install Qt6 using aqtinstall.")
    logger.info("    Set to something other than TRUE if you wish to use an already installed version of Qt6.")
    logger.info(
        "    But then you'll need to set QT_DIR env variable to your Qt6 installation before running run-cmake.bat."
    )
    logger.info(field(f"* IFCOS_NUM_BUILD_PROCS\t= {ifcos_num_build_procs}"))
    logger.info("  - How many MSBuild.exe processes may be run in parallel.")
    logger.info("    Defaults to NUMBER_OF_PROCESSORS. Used also by other IfcOpenShell build scripts.\n")


def print_success(start_time: datetime) -> None:
    logger.info("")
    logger.info(colorize(f"{PROJECT_NAME} dependencies built.", C.GREEN))

    end_time = datetime.now().replace(microsecond=0)
    logger.info("")
    logger.info(f"Build ended at {end_time}. Time elapsed {end_time - start_time}.")


def parse_args() -> Args:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
    # SUPPRESS avoids a misleading "(default: None)" in `--help`,
    # though then arg might not be set and we use `getattr` to get it.
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
        "build_type",
        nargs="?",
        default=argparse.SUPPRESS,
        choices=BUILD_TYPES,
        help=f"Build type. (default: {BUILD_TYPE_DEFAULT})",
    )
    parser.add_argument(
        "--build-type",
        dest="build_type_flag",
        default=BUILD_TYPE_DEFAULT,
        choices=BUILD_TYPES,
        help="Alternative way to specify the build type, instead of the positional argument.",
    )
    parser.add_argument(
        "--log-level",
        # TODO: relax default to INFO once things get more stable.
        default="DEBUG",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--reuse-boost",
        action="store_true",
        help=(
            "Skip building Boost if it's already installed from this script's previous runs, instead of always rebuilding it. "
            "Speeds up the build a bit when iterating/debugging this script."
        ),
    )
    parser.add_argument(
        "--num-build-procs",
        dest="num_build_procs",
        type=int,
        default=argparse.SUPPRESS,
        help=HelpStrings.NUM_BUILD_PROCS,
    )
    parser.add_argument(
        "--install-python",
        dest="install_python",
        action=argparse.BooleanOptionalAction,
        default=argparse.SUPPRESS,
        help=(
            "Download and install Python. If disabled, an already installed Python is used - "
            "set the PYTHONHOME env variable to its installation path before running run-cmake.bat. "
            "Also can be specified by using IFCOS_INSTALL_PYTHON env variable. "
            "(default: True)"
        ),
    )
    parser.add_argument(
        "--install-qt6",
        dest="install_qt6",
        action=argparse.BooleanOptionalAction,
        default=argparse.SUPPRESS,
        help=(
            "Download and install Qt6 using aqtinstall. If disabled, an already installed Qt6 is used - "
            "set the QT_DIR env variable to its installation path before running run-cmake.bat. "
            "Also can be specified by using IFCOS_INSTALL_QT6 env variable. "
            "(default: True)"
        ),
    )
    args = parser.parse_args()
    logger.setLevel(args.log_level)

    if args.generator is not None and args.generator_flag is not None:
        parser.error("generator was specified both as a positional argument and as --generator.")
    generator = args.generator or args.generator_flag

    build_cfg = getattr(args, "build_cfg", None) or args.build_cfg_flag
    build_type = getattr(args, "build_type", None) or args.build_type_flag

    num_build_procs = getattr(args, "num_build_procs", None) or int(
        os.getenv("IFCOS_NUM_BUILD_PROCS") or multiprocessing.cpu_count()
    )
    install_python = getattr(args, "install_python", None)
    if install_python is None:
        install_python = is_on_off(os.getenv("IFCOS_INSTALL_PYTHON"), default=True)
    install_qt6 = getattr(args, "install_qt6", None)
    if install_qt6 is None:
        install_qt6 = is_on_off(os.getenv("IFCOS_INSTALL_QT6"), default=True)

    return Args(
        generator=generator,
        build_cfg=build_cfg,
        build_type=build_type,
        reuse_boost=args.reuse_boost,
        num_build_procs=num_build_procs,
        install_python=install_python,
        install_qt6=install_qt6,
    )


def main() -> None:
    ARGS = parse_args()

    logger.info(f"This script fetches and builds all {PROJECT_NAME} dependencies\n")

    ensure_script_dir()

    # Make sure vcvarsall.bat is called and dev env set is up.
    get_vs_var("VSINSTALLDIR")

    # Check for cl.exe - at least the "Typical" Visual Studio 2015 installation does not include the C++ toolset by default,
    # http://blogs.msdn.com/b/vcblog/archive/2015/07/24/setup-changes-in-visual-studio-2015-affecting-c-developers.aspx
    if not shutil.which("cl"):
        logger.error(
            "cl.exe not in PATH. Make sure to select the C++ toolset when installing Visual Studio- cannot proceed."
        )
        sys.exit(1)

    vs_cfg_vars = vs_cfg(ARGS.generator, REPO_ROOT)
    build_deps_cache = BuildDepsCache(vs_cfg_vars)

    # Cache last used CMake generator and configurable dependency dirs for other scripts to use.
    build_deps_cache.add_entry("GEN_SHORTHAND", vs_cfg_vars.gen_shorthand)

    # Make sure deps and install folders exists.
    vs_cfg_vars.deps_dir.mkdir(parents=True, exist_ok=True)
    vs_cfg_vars.install_dir.mkdir(parents=True, exist_ok=True)

    # Note BUILD_TYPE not passed, Clean e.g. wouldn't delete the installed files.
    # TODO: consider inlining.
    MSBUILD_MULTIPROC = (
        "/m",
        f"/p:CL_MPCount={ARGS.num_build_procs}",
        "/p:UseMultiToolTask=true",
        "/p:EnforceProcessCountAcrossBuilds=true",
    )
    MSBUILD_CMD = ("MSBuild.exe", "/nologo", *MSBUILD_MULTIPROC)

    # Check that required tools are in PATH.
    # TODO: drop "powershell" later.
    REQUIRED_COMMANDS = ("powershell", "git", "cmake", "7z")
    for command in REQUIRED_COMMANDS:
        require_command(command)

    validate_cmake_version()

    print_build_config(
        vs_cfg_vars,
        ARGS.build_cfg,
        ARGS.build_type,
        ARGS.install_python,
        ARGS.install_qt6,
        ARGS.num_build_procs,
    )

    logger.warning("Warning: You will need roughly 8 GB of disk space to proceed.\n")
    logger.info(
        "If you are not ready with the above: type 'n' in the prompt below. Build proceeds on all other inputs!"
    )
    # TODO: add a `-y` option to skip this prompt.
    do_continue = input("> ")
    if do_continue == "n":
        sys.exit(0)

    START_TIME = datetime.now().replace(microsecond=0)
    logger.info(f"Build started at {START_TIME}.")

    nuget_exe = install_nuget(vs_cfg_vars.deps_dir)
    install_ccache(vs_cfg_vars.deps_dir, nuget_exe, build_deps_cache)
    install_proj(vs_cfg_vars, ARGS.build_type, ARGS.build_cfg, MSBUILD_MULTIPROC)
    install_mpir(vs_cfg_vars, vs_cfg_vars.deps_dir, vs_cfg_vars.install_dir, ARGS.build_cfg)
    install_mpfr(
        vs_cfg_vars, vs_cfg_vars.deps_dir, vs_cfg_vars.install_dir, ARGS.build_cfg, ARGS.build_type, MSBUILD_CMD
    )
    install_boost(vs_cfg_vars, build_deps_cache, ARGS.build_cfg, ARGS.num_build_procs, ARGS.reuse_boost)
    install_json(vs_cfg_vars.install_dir)
    install_opencollada(vs_cfg_vars, ARGS.build_type, ARGS.build_cfg, MSBUILD_MULTIPROC)
    install_occt(vs_cfg_vars, ARGS.build_type, build_deps_cache, ARGS.build_cfg, MSBUILD_MULTIPROC)
    pythonhome = install_python(vs_cfg_vars, ARGS.install_python, build_deps_cache, nuget_exe)
    install_swig(vs_cfg_vars, ARGS.build_type, build_deps_cache, MSBUILD_MULTIPROC)
    install_cgal(vs_cfg_vars, ARGS.build_type, ARGS.build_cfg, MSBUILD_MULTIPROC)
    install_eigen(vs_cfg_vars)
    install_zstd(vs_cfg_vars, ARGS.build_type, ARGS.build_cfg, MSBUILD_MULTIPROC)
    install_rocksdb(vs_cfg_vars, ARGS.build_type, ARGS.build_cfg, MSBUILD_MULTIPROC)
    install_qt6(vs_cfg_vars, build_deps_cache, ARGS.build_cfg, ARGS.install_qt6, pythonhome)
    install_manifold(vs_cfg_vars, ARGS.build_type, build_deps_cache, ARGS.build_cfg, MSBUILD_MULTIPROC)

    print_success(START_TIME)


if __name__ == "__main__":
    main()
