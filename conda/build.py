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
    "RECIPE_DIR",
    "PKG_VERSION",
    "PREFIX",
    "LIBRARY_PREFIX",
    # Python executable in the host prefix.
    "PYTHON",
    # E.g. "3.12".
    "PY_VER",
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
        SO_SUFFIX = "dylib"
        build_env["LDFLAGS"] = f"{os.environ.get('LDFLAGS', '')} -Wl,-undefined,dynamic_lookup"
    elif WIN:
        SO_SUFFIX = "lib"  # Import library used for linking.
    else:
        SO_SUFFIX = "so"

    PY_VER = get_conda_var("PY_VER")
    # Remove dot from PY_VER for use in library name.
    PY_VER_NODOT = PY_VER.replace(".", "")

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
        f"-DOCC_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include' / 'opencascade'}",
        f"-DOCC_LIBRARY_DIR:FILEPATH={DEPENDENCY_PREFIX / 'lib'}",
        f"-DJSON_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include'}",
        f"-DEIGEN_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include' / 'eigen3'}",
        f"-DCGAL_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include'}",
        f"-DLIBXML2_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include' / 'libxml2'}",
        f"-DLIBXML2_LIBRARIES:FILEPATH={DEPENDENCY_PREFIX / 'lib' / f'libxml2.{SO_SUFFIX}'}",
        f"-DPYTHON_EXECUTABLE:FILEPATH={get_conda_var('PYTHON')}",
        f"-DGMP_LIBRARY_DIR:FILEPATH={DEPENDENCY_PREFIX / 'lib'}",
        f"-DMPFR_LIBRARY_DIR:FILEPATH={DEPENDENCY_PREFIX / 'lib'}",
    ]
    if WIN:
        PREFIX = Path(get_conda_var("PREFIX"))
        cmake_command += [
            f"-DGMP_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include'}",
            f"-DPYTHON_INCLUDE_DIR:FILEPATH={PREFIX / 'include'}",
            f"-DPYTHON_LIBRARY:FILEPATH={PREFIX / 'libs' / f'python{PY_VER_NODOT}.lib'}",
            f"-DBoost_LIBRARY_DIR:FILEPATH={DEPENDENCY_PREFIX / 'lib'}",
            f"-DBoost_INCLUDE_DIR:FILEPATH={DEPENDENCY_PREFIX / 'include'}",
        ]
    run(cmake_command, env=build_env)
    run(["cmake", "--build", str(BUILD_DIR), "-j", get_conda_var("CPU_COUNT")])
    run(["cmake", "--install", str(BUILD_DIR)])
    run(
        [
            sys.executable,
            str(Path(get_conda_var("RECIPE_DIR")) / "update_version_init.py"),
            get_conda_var("PKG_VERSION"),
            str(Path(get_conda_var("SP_DIR")) / "ifcopenshell" / "__init__.py"),
        ]
    )


if __name__ == "__main__":
    main()
