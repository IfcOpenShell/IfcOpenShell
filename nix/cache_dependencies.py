# /// script
# ///
"""
Cache built dependencies for builds.

This script is finding common install directory and either
packs each folder into a tar.gz archive, if it wasn't packed before,
or unpacks existing archives.

Expected to be executed from 'build' directory (e.g. that might contain 'Linux/x86_64/install').

Usage: python cache_dependencies.py [pack|unpack]
"""

import platform
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Literal

CACHE_PREFIX = "cache-"


def get_install_dir() -> Path:
    if platform.system() == "Darwin":
        pattern = "Darwin/*/*/install"
    else:
        pattern = "*/*/install"
    for data in Path.cwd().glob(pattern):
        return data
    raise Exception("No install dir found")


def run(cmd: str) -> None:
    print(f"Running command: `{cmd}`")
    subprocess.check_call(cmd, shell=True)


def pack_dependencies(install_dir: Path) -> None:
    # Process each install_dir
    for dependency_path in install_dir.iterdir():
        if not dependency_path.is_dir():
            continue
        dependency_name = dependency_path.name
        # Skip ifcopenshell - it's a build output, not a dependency to reuse across builds.
        if dependency_name == "ifcopenshell":
            continue
        tar_path = install_dir / f"{CACHE_PREFIX}{dependency_name}.tar.gz"
        if tar_path.exists():
            print(f"Skipping existing cache: '{tar_path}'")
        else:
            # Python's `tarfile` is 10x slower than `tar` cli, so we use `tar`.
            run(f'tar -czf "{tar_path}" -C "{install_dir}" "{dependency_name}"')
            print(f"Created cache: '{tar_path}'")


def unpack_dependencies(install_dir: Path) -> None:
    # `filter` argument was fully introduced in 3.12
    # and results in deprecation warnings in 3.12-3.13, if not provided.
    tar_filter: dict[Literal["filter"], Literal["data"]] = (
        {"filter": "data"} if bool(sys.version_info >= (3, 12)) else {}
    )
    for tar_path in install_dir.glob(f"{CACHE_PREFIX}*.tar.gz"):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=install_dir, **tar_filter)
        print(f"Extracted cache: '{tar_path.name}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or (action := sys.argv[1].lower()) not in ("pack", "unpack"):
        print(__doc__)
        sys.exit(1)

    install_dir = get_install_dir()
    print(f"Found install dir: '{install_dir}'")

    if action == "pack":
        pack_dependencies(install_dir)
    else:
        unpack_dependencies(install_dir)
