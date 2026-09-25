# /// script
# ///
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Literal

WIN = sys.platform == "win32"
MAC = sys.platform == "darwin"
UNIX = not WIN

CondaVar = Literal[
    # Defines:
    # - CMAKE_BUILD_TYPE=Release
    # - CMAKE_INSTALL_PREFIX (depends on the platform)
    "CMAKE_ARGS",
    "CPU_COUNT",
    "PKG_VERSION",
    "PREFIX",
    "LIBRARY_PREFIX",
    # Python site-packages directory in the host prefix.
    "SP_DIR",
]


def get_conda_var(var: CondaVar) -> str:
    return os.environ[var]


def run(args: list[str], env: dict[str, str] | None = None) -> None:
    print(f"$ {shlex.join(args)}")
    subprocess.check_call(args, env={**os.environ, **env} if env else None)


def main() -> None:
    build_env: dict[str, str] = {}
    if MAC:
        build_env["LDFLAGS"] = f"{os.environ.get('LDFLAGS', '')} -Wl,-undefined,dynamic_lookup"

    REPO_ROOT = Path.cwd()
    BUILD_DIR = Path("build")
    # Where host dependencies (libs, headers) are installed.
    DEPENDENCY_PREFIX = Path(get_conda_var("LIBRARY_PREFIX" if WIN else "PREFIX"))
    BUILD_DIR.mkdir(exist_ok=True)

    cmake_command = [
        "cmake",
        "-G",
        "Ninja",
        "-S",
        str(REPO_ROOT / "cmake"),
        "-B",
        str(BUILD_DIR),
        *shlex.split(get_conda_var("CMAKE_ARGS"), posix=UNIX),
        "-DSCHEMA_VERSIONS:STRING=2x3;4;4x1;4x3_add2",
        "-DBUILD_EXAMPLES:BOOL=OFF",
        "-DBUILD_GEOMSERVER:BOOL=OFF",
        "-DBUILD_IFCPYTHON:BOOL=ON",
        "-DBUILD_IFCGEOM:BOOL=ON",
        "-DBUILD_CONVERT:BOOL=ON",
        "-DBUILD_IFCMAX:BOOL=OFF",
        "-DCOLLADA_SUPPORT:BOOL=OFF",
        "-DGLTF_SUPPORT:BOOL=ON",
        # Dependencies.
        "-DBoost_USE_STATIC_LIBS:BOOL=OFF",
        f"-DCMAKE_PREFIX_PATH:FILEPATH={DEPENDENCY_PREFIX}",
        f"-DCMAKE_SYSTEM_PREFIX_PATH:FILEPATH={DEPENDENCY_PREFIX}",
    ]

    if MAC:
        # Qt6 is pulled in by VTK (via OCCT). Older conda-forge osx-arm64 qt6-main builds
        # (6.8.3 build <3) were cross-compiled and require QT_HOST_PATH in find_package(Qt6).
        # See https://github.com/conda-forge/qt-main-feedstock/issues/273.
        # TODO: drop once qt starts to resolve to 6.8.4, currently it resolves 6.8.3
        # by some tricky dependency chain.
        cmake_command.append("-DQT_REQUIRE_HOST_PATH_CHECK:BOOL=OFF")

    run(cmake_command, env=build_env)
    run(["cmake", "--build", str(BUILD_DIR), "-j", get_conda_var("CPU_COUNT")])
    run(["cmake", "--install", str(BUILD_DIR)])

    init_path = Path(get_conda_var("SP_DIR")) / "ifcopenshell" / "__init__.py"
    version = get_conda_var("PKG_VERSION")
    init_path.write_text(
        init_path.read_text(encoding="utf-8").replace('version = "0.0.0"', f'version = "{version}"'),
        encoding="utf-8",
    )
    print(f"Updated version in {init_path} to {version}")


if __name__ == "__main__":
    main()
