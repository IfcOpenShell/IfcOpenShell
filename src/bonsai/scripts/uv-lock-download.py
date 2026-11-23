#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.15"
# dependencies = [
#     "packaging>=26.1",
# ]
# [tool.ty.environment]
# root = ["."]
# # find `common.py`.
# extra-paths = ["../../../win"]
# ///
"""Download Bonsai's dependency wheels for a target platform and Python version.

Wheels are selected from the provided `uv.lock` (e.g. `src/bonsai/bundled-wheels/uv.lock`).

This script is needed because there's no tool to download the wheels from `uv.lock`.
There's no `uv download` and `pip download -r pylock.toml` doesn't support `--platform`.
"""

import argparse
import hashlib
import logging
import re
import subprocess
import sys
import tomllib
import urllib.request
from pathlib import Path
from typing import Literal, NamedTuple, get_args

from packaging.markers import Environment, default_environment
from packaging.pylock import PackageDirectory, PackageSdist, PackageWheel, Pylock
from packaging.tags import Tag, compatible_tags, cpython_tags, mac_platforms

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "win"))

from common import logger

logger.setLevel(logging.DEBUG)

Platform = Literal["linux", "win", "macosm1"]


def darwin_platform_release(lock: Pylock) -> str:
    """Parse the `platform_release` lower bound from the lock's darwin environment marker.

    It's already hardcoded in `pyproject.toml` and then it's written to `pylock.toml`,
    so we're parsing it, instead of hardocing it here too.
    """
    darwin_marker = next(str(marker) for marker in lock.environments or [] if 'sys_platform == "darwin"' in str(marker))
    match = re.search(r'platform_release >= "([^"]+)"', darwin_marker)
    assert match, darwin_marker
    return match.group(1)


def target_environment(lock: Pylock, platform: Platform, python_minor: int) -> Environment:
    sys_platforms: dict[Platform, str] = {
        "win": "win32",
        "linux": "linux",
        "macosm1": "darwin",
    }

    platform_machines: dict[Platform, str] = {
        "win": "AMD64",
        "linux": "x86_64",
        "macosm1": "arm64",
    }

    env = default_environment()
    # Environment has many more fields, but we just cover here the ones we actually use in our markers.
    env["sys_platform"] = sys_platforms[platform]
    env["platform_machine"] = platform_machines[platform]
    if platform == "macosm1":
        env["platform_release"] = darwin_platform_release(lock)
    env["python_full_version"] = f"3.{python_minor}.0"
    return env


def target_tags(lock: Pylock, project_dir: Path, platform: Platform, python_minor: int) -> list[Tag]:
    """Build the wheel tags for the target, most preferred first.

    Just as `pip download`, `Pylock.selects` required to list all platform tags,
    not just minimum supported version.
    """

    def darwin_to_macos_major(darwin: int) -> int:
        # Darwin 20-24 are macOS 11-15, then Apple jumped to macOS 26 (Tahoe) at Darwin 25.
        return darwin - 9 if darwin < 25 else darwin + 1

    def manylinux_platforms() -> list[str]:
        # Reuse `minimum-libc-version` from `pyproject.toml`, instead of hardcoding it here too.
        pyproject = tomllib.loads((project_dir / "pyproject.toml").read_text())
        glibc = pyproject["tool"]["uv"]["minimum-libc-version"]["glibc"]
        glibc_minor = int(glibc.split(".")[1])
        # glibc 2.17 is the oldest version possible.
        platforms = [f"manylinux_2_{minor}_x86_64" for minor in reversed(range(17, glibc_minor + 1))]
        platforms.append("manylinux2014_x86_64")
        return platforms

    match platform:
        case "win":
            platforms = ["win_amd64"]
        case "linux":
            platforms = manylinux_platforms()
        case "macosm1":
            macos_major = darwin_to_macos_major(int(darwin_platform_release(lock)))
            platforms = list(mac_platforms((macos_major, 0), "arm64"))
    python_version = (3, python_minor)
    return [
        *cpython_tags(python_version, platforms=platforms),
        *compatible_tags(python_version, f"cp3{python_minor}", platforms),
    ]


def download_wheel(wheel: PackageWheel, dest: Path) -> None:
    """Download the wheel into `dest` and verify its sha256 hash.

    Skips the download if the wheel already exists in `dest` with the expected hash.
    """
    assert wheel.url is not None, wheel.filename
    expected_hash = wheel.hashes["sha256"]
    path = dest / wheel.filename

    # Reuse downloaded wheels.
    if path.exists():
        with path.open("rb") as file:
            existing_hash = hashlib.file_digest(file, "sha256").hexdigest()
        if existing_hash == expected_hash:
            logger.info("Already downloaded %s", wheel.filename)
            return
        logger.warning("Hash mismatch for existing %s, downloading it again", wheel.filename)

    logger.info("Downloading %s", wheel.filename)
    digest = hashlib.sha256()
    with urllib.request.urlopen(wheel.url, timeout=60) as response, path.open("wb") as file:
        while chunk := response.read(1 << 16):
            digest.update(chunk)
            file.write(chunk)

    # Validate wheel hash.
    if digest.hexdigest() != expected_hash:
        path.unlink()
        raise ValueError(f"Hash mismatch for {wheel.url}: expected {expected_hash}, got {digest.hexdigest()}")


class Args(NamedTuple):
    lock: Path
    targets: list[tuple[Platform, int]]
    """Platform and Python 3 minor version pairs, e.g. `("linux", 11)` for Python 3.11 on Linux."""
    dest: Path | None
    """Output directory for the downloaded wheels, `None` to only check that wheels are available."""


def parse_python_minors(value: str) -> list[int]:
    return [int(python_minor) for python_minor in value.split(",")]


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--lock", type=Path, required=True, help="Path to uv.lock, its directory should also contain pyproject.toml"
    )
    parser.add_argument("--platform", choices=get_args(Platform))
    parser.add_argument("--python", type=int, help="Python 3 minor version, e.g. 11 for Python 3.11")
    parser.add_argument("--dest", type=Path, help="Output directory for the downloaded wheels")
    parser.add_argument(
        "--matrix-check",
        type=parse_python_minors,
        help=(
            "Comma separated Python 3 minor versions, e.g. 11,13; "
            "checks that wheels are available for every platform for each of them, without downloading. "
            "Takes priority over other args"
        ),
    )
    args = parser.parse_args()

    if args.matrix_check is not None:
        return Args(
            lock=args.lock,
            targets=[(platform, python_minor) for platform in get_args(Platform) for python_minor in args.matrix_check],
            dest=None,
        )

    if args.platform is None or args.python is None or args.dest is None:
        parser.error("--platform, --python and --dest are required, unless --matrix-check is used")
    return Args(lock=args.lock, targets=[(args.platform, args.python)], dest=args.dest)


def main() -> None:
    args = parse_args()
    # Script is using `pylock.toml` instead of `uv.lock`, because
    # - `uv.lock` is undocumented and internal format to uv
    # - `pylock.toml` is public and `packaging.pylock` has a clear way to parse it
    # and resolve environments using it.
    # Project with the bundled wheels, containing `pyproject.toml` and `uv.lock`.
    project_dir = args.lock.parent
    result = subprocess.run(
        ["uv", "export", "--locked", "--format", "pylock.toml"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    lock = Pylock.from_dict(tomllib.loads(result.stdout))

    if args.dest is not None:
        args.dest.mkdir(parents=True, exist_ok=True)

    for platform, python_minor in args.targets:
        logger.info("Target: %s, Python 3.%s", platform, python_minor)
        env = target_environment(lock, platform, python_minor)
        logger.info("Selecting for environment: %s", env)
        tags = target_tags(lock, project_dir, platform, python_minor)

        for package, dist in lock.select(environment=env, tags=tags):
            # `select` falls back to sdists when no wheel matches the tags, but we only want wheels.
            # Should never happen in theory, since we have `no-build` in `pyproject.toml`.
            assert not isinstance(dist, PackageSdist), package.name

            if isinstance(dist, PackageDirectory):
                # Our package itself.
                continue
            assert isinstance(dist, PackageWheel)
            assert dist.url is not None, package.name
            logger.debug("Found wheel for %s: %s", package.name, dist.url)

            if args.dest is not None:
                download_wheel(dist, args.dest)


if __name__ == "__main__":
    main()
