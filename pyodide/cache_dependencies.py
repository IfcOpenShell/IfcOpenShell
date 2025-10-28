"""
Cache built dependencies for builds.

This script is finding common install directory and either
packs each folder into a tar.gz archive, if it wasn't packed before,
or unpacks existing archives.

Usage: python cache_dependencies.py [pack|unpack]
"""

import tarfile
import sys
from pathlib import Path
from typing import Literal


CACHE_PREFIX = "cache-"


def get_install_dir() -> Path:
    for data in Path.cwd().glob("*/*/install"):
        return data
    raise Exception("No install dir found")


def pack_dependencies(install_dir: Path) -> None:
    # Process each install_dir
    for dependency_path in install_dir.iterdir():
        if not dependency_path.is_dir():
            continue
        dependency_name = dependency_path.name
        tar_path = install_dir / f"{CACHE_PREFIX}{dependency_name}.tar.gz"
        if tar_path.exists():
            print(f"Skipping existing cache: '{tar_path}'")
        else:
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(dependency_path, arcname=dependency_path.name)
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
