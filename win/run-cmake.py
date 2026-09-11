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
import os
import sys
from itertools import chain
from pathlib import Path
from typing import Literal, NamedTuple, NoReturn

from common import (
    OFF_ON,
    PROJECT_NAME,
    REPO_ROOT,
    BuildDepsCache,
    C,
    HelpStrings,
    colorize,
    ensure_script_dir,
    logger,
    resolve_generator,
    run,
    run_streamed,
)
from vs_cfg import VsCfgResult, vs_cfg


class Dep(NamedTuple):
    env_var: str
    rel_path: Path | None
    cmake_prefix: bool = True
    """Whether the dep's dir should be added to CMAKE_PREFIX_PATH."""
    pass_to_env: bool = False
    """Whether `env_var` should be added to the subprocess env passed to cmake."""
    required: bool = True
    """Whether to error out if the dep's value can't be resolved."""
    base: Literal["DEPS", "INSTALL"] = "INSTALL"
    """Which base dir `rel_path` is relative to."""


class Deps:
    DEPS: dict[str, Dep] = {
        "boost": Dep("BOOST_INSTALL_DIR", None),
        "occ": Dep("OCC_INSTALL_DIR", None),
        "opencollada": Dep("OPENCOLLADA_INSTALL_DIR", Path("OpenCOLLADA")),
        # We don't install Eigen currently,
        # so there's no Eigen3config.cmake and therefore we provide path explicitly.
        "eigen": Dep("EIGEN_DIR", Path("Eigen"), cmake_prefix=False, pass_to_env=True),
        "cgal": Dep("CGAL_INSTALL_DIR", Path("cgal")),
        "gmp": Dep("GMP_INSTALL_DIR", Path("mpir")),
        "mpfr": Dep("MPFR_INSTALL_DIR", Path("mpfr")),
        # CCACHE_INSTALL_DIR is only set when ccache wasn't found on PATH.
        "ccache": Dep("CCACHE_INSTALL_DIR", None, required=False),
        "zstd": Dep("ZSTD_INSTALL_DIR", Path("zstd")),
        "swig": Dep("SWIG_INSTALL_DIR", None),
        "rocksdb": Dep("ROCKSDB_INSTALL_DIR", Path("rocksdb")),
        "json": Dep("JSON_INCLUDE_DIR", Path("json"), cmake_prefix=False, pass_to_env=True),
        "libxml2_libraries": Dep(
            "LIBXML2_LIBRARIES", Path("OpenCOLLADA/lib/opencollada/xml.lib"), cmake_prefix=False, pass_to_env=True
        ),
        "libxml2_include_dir": Dep(
            "LIBXML2_INCLUDE_DIR",
            Path("OpenCOLLADA/Externals/LibXML/include"),
            cmake_prefix=False,
            pass_to_env=True,
            base="DEPS",
        ),
        # TODO: drop this TRANSITION check once everyone has re-run build-deps.py with manifold support.
        "manifold": Dep("MANIFOLD_INSTALL_PATH", None, required=False),
        "pythonhome": Dep("PYTHONHOME", None, cmake_prefix=False),
    }

    _values: dict[str, Path | None] | None = None

    @classmethod
    def values(cls) -> dict[str, Path | None]:
        if cls._values is None:
            raise RuntimeError("Deps.values() accessed before Deps.init_values() was called.")
        return cls._values

    @classmethod
    def init_values(cls, vs_cfg_vars: VsCfgResult, deps_cache: dict[str, str]) -> None:
        cls._values = {}
        has_errors = False
        for name, dep in cls.DEPS.items():
            if dep.rel_path is not None:
                base_dir = vs_cfg_vars.install_dir if dep.base == "INSTALL" else vs_cfg_vars.deps_dir
                value = base_dir / dep.rel_path
            else:
                value = get_var(deps_cache, dep.env_var, deps_cache_only=True)
                if isinstance(value, str):
                    value = Path(value)
            if dep.required:
                if value is None:
                    logger.error(f"{dep.env_var} is required but could not be resolved.")
                    has_errors = True
                elif not value.exists():
                    logger.error(f"{dep.env_var} does not exist: {value}")
                    has_errors = True
            cls._values[name] = value
        if has_errors:
            sys.exit(1)

    @classmethod
    def cmake_prefix_paths(cls) -> list[Path]:
        return [
            value for name, dep in cls.DEPS.items() if dep.cmake_prefix and (value := cls.values()[name]) is not None
        ]

    @classmethod
    def env_dict(cls) -> dict[str, str]:
        return {dep.env_var: str(cls.values()[name]) for name, dep in cls.DEPS.items() if dep.pass_to_env}


def get_var(deps_cache: dict[str, str], key: str, *, deps_cache_only: bool = False) -> str | None:
    # TODO: just rely on `deps_cache`?
    if deps_cache_only:
        return deps_cache.get(key)
    return deps_cache.get(key) or os.environ.get(key)


class Args(NamedTuple):
    generator: str | None
    extra_args: list[str]


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # TODO: same as in build-ifcopenshell.py, can be removed later.
        if message.startswith("unrecognized arguments"):
            message += (
                "\nHint: put args meant for CMake after '--', e.g. `run-cmake.py vs2022-x64 -- -DGLTF_SUPPORT=ON`."
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
        help=HelpStrings.generator("GEN_SHORTHAND from the most recently modified BuildDepsCache-*.txt is used"),
    )
    parser.add_argument(
        "--generator",
        dest="generator_flag",
        default=None,
        help=HelpStrings.GENERATOR_FLAG,
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

    return Args(generator=generator, extra_args=extra_args)


def main() -> None:
    ARGS = parse_args()

    ensure_script_dir()

    explicit_generator = ARGS.generator is not None
    generator = resolve_generator(ARGS.generator)

    vs_cfg_vars = vs_cfg(generator, REPO_ROOT)

    deps_cache = BuildDepsCache.parse(vs_cfg_vars.build_deps_cache_path)

    Deps.init_values(vs_cfg_vars, deps_cache)

    pythonhome = Deps.values()["pythonhome"]
    assert pythonhome is not None
    python_executable = f"{pythonhome}\\python.exe"
    py_ver_major_minor = run(
        python_executable, "-c", "import sys; print(f'{sys.version_info[0]}{sys.version_info[1]}')"
    ).strip()
    python_include_dir = f"{pythonhome}\\include"
    python_library = f"{pythonhome}\\libs\\python{py_ver_major_minor}.lib"

    # TODO: add as cli arg.
    ADD_COMMIT_SHA = OFF_ON[bool(os.getenv("ADD_COMMIT_SHA"))]
    VERSION_OVERRIDE = ADD_COMMIT_SHA

    qt_dir = get_var(deps_cache, "QT_DIR") or get_var(deps_cache, "QT6_INSTALL_DIR")
    qt_host_path = get_var(deps_cache, "QT_HOST_PATH") or get_var(deps_cache, "QT6_HOST_INSTALL_DIR")

    cmake_install_prefix = REPO_ROOT / f"_installed-{vs_cfg_vars.gen_shorthand}"

    logger.info("")
    logger.info(colorize("Script configuration:", C.PURPLE))
    logger.info(f"  Generator    = {generator}")
    logger.info(f"  Architecture = {vs_cfg_vars.vs_platform}")
    logger.info(f"  Toolset      = {vs_cfg_vars.vs_toolset_override}")
    logger.info(f"  Arguments    = {ARGS.extra_args}")
    logger.info("")

    # Some deps are a bit less trivial to get, so we calculate them outside `Deps`.
    extra_vars: dict[str, object] = {
        "PYTHON_INCLUDE_DIR": python_include_dir,
        "PYTHON_LIBRARY": python_library,
        "PYTHON_EXECUTABLE": python_executable,
        "QT_DIR": qt_dir,
        "QT_HOST_PATH": qt_host_path,
        "CMAKE_INSTALL_PREFIX": cmake_install_prefix,
    }
    dep_vars = ((dep.env_var, Deps.values()[name]) for name, dep in Deps.DEPS.items())
    logger.info(colorize(f"Dependency Environment Variables for {PROJECT_NAME}:", C.PURPLE))
    for env_var, value in chain(dep_vars, extra_vars.items()):
        logger.info(f"   {env_var:<23} = {value}")
    logger.info("")

    build_dir = REPO_ROOT / vs_cfg_vars.build_dir
    build_dir.mkdir(parents=True, exist_ok=True)

    cmakelists_dir = REPO_ROOT / "cmake"
    if explicit_generator:
        cmake_cache_path = build_dir / "CMakeCache.txt"
        if cmake_cache_path.exists():
            cmake_cache_path.unlink()
    logger.info(f'"Running CMake for {PROJECT_NAME}."')

    cmake_prefix_path_parts = Deps.cmake_prefix_paths()
    if qt_dir:
        cmake_prefix_path_parts.append(qt_dir)
    cmake_prefix_path = ";".join(str(part) for part in cmake_prefix_path_parts)

    # TODO: add cli arg.
    use_ninja = os.getenv("USE_NINJA")
    if use_ninja:
        cmake_generator = "Ninja"
        arch_option = ()
    else:
        cmake_generator = vs_cfg_vars.generator.name
        arch_option = ("-A", vs_cfg_vars.vs_platform)

    cmake_args = [
        str(cmakelists_dir),
        "-G",
        cmake_generator,
        *arch_option,
        f"-DCMAKE_INSTALL_PREFIX={cmake_install_prefix}",
        "-DWITH_ROCKSDB=ON",
        "-DWITH_ZSTD=ON",
        f"-DCMAKE_PREFIX_PATH={cmake_prefix_path}",
        f"-DADD_COMMIT_SHA={ADD_COMMIT_SHA}",
        f"-DVERSION_OVERRIDE={VERSION_OVERRIDE}",
    ]
    if qt_dir:
        cmake_args.append(f"-DQT_DIR={qt_dir}")
    if qt_host_path:
        cmake_args.append(f"-DQT_HOST_PATH={qt_host_path}")
    if Deps.values()["manifold"]:
        cmake_args.append("-DWITH_MANIFOLD=ON")
    cmake_args += ARGS.extra_args

    run_streamed(
        "cmake",
        *cmake_args,
        cwd=build_dir,
        env={
            **Deps.env_dict(),
            "PYTHONHOME": str(pythonhome),
            "PYTHON_EXECUTABLE": str(python_executable),
            "PYTHON_INCLUDE_DIR": str(python_include_dir),
            "PYTHON_LIBRARY": str(python_library),
        },
    )

    logger.info("")


if __name__ == "__main__":
    main()
