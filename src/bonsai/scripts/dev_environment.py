#!/usr/bin/env python3
# /// script
# ///
"""Setup Bonsai Development Environment.

Script links existing Bonsai installation to the provided IfcOpenShell repository.

If Bonsai is installed from unstable repo (raw_githubusercontent_com) and this script is already part
of IfcOpenShell repo you want to link, then you can just run it and it will just work.

Otherwise, see the SETTINGS section below to validate script settings to ensure it fits your environment.

Example usage:

    python /xxx/yyy/dev_environment.py
    python dev_environment.py

"""

import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import NamedTuple

available_platforms = ("win32", "darwin", "linux")
if sys.platform not in available_platforms:
    print(f"Currently only available on {', '.join(available_platforms)}. Not available on {sys.platform}.")
    exit(1)

if sys.platform == "win32":
    BLENDER_CONFIG_PATH = Path.home() / "AppData/Roaming/Blender Foundation/Blender"
elif sys.platform == "darwin":
    BLENDER_CONFIG_PATH = Path.home() / "Library/Application Support/Blender"
elif sys.platform == "linux":
    BLENDER_CONFIG_PATH = Path.home() / ".config/blender"
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

existing_versions = []
if BLENDER_CONFIG_PATH.exists():
    existing_versions = sorted((p.name for p in BLENDER_CONFIG_PATH.iterdir() if p.is_dir()), reverse=True)

if not existing_versions:
    print(f"No existing Blender versions found in '{BLENDER_CONFIG_PATH}'. Install Blender first.")
    exit(1)


BINARIES_SOURCE_DESCRIPTIONS = {
    "installed": "From the installed Bonsai. They will be copied to the repo, replacing the ones already there.",
    "compiled": "I compile IfcOpenShell myself. The binaries in the repo will be used as they are.",
}


class Args(NamedTuple):
    blender_version: str | None
    binaries_source: str | None
    repo_path: str | None


def parse_args() -> Args:
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "--blender-version",
        choices=existing_versions,
        help="Blender version. Will be prompted if not set.",
    )
    arg_parser.add_argument(
        "--binaries-source",
        choices=tuple(BINARIES_SOURCE_DESCRIPTIONS),
        help="Where the IfcOpenShell binaries come from ({}). Will be prompted if not set.".format(
            "; ".join(f"{k}: {v}" for k, v in BINARIES_SOURCE_DESCRIPTIONS.items())
        ),
    )
    arg_parser.add_argument(
        "--repo-path",
        help="Path to your local IfcOpenShell repository. Deduced from this script's location if not set.",
    )
    namespace = arg_parser.parse_args()
    return Args(**vars(namespace))


ARGS = parse_args()

# ---------------------------
# SETTINGS.
# ---------------------------
# BLENDER_PATH: Path to Blender's configuration folder.
# User will be prompted for the Blender version, unless provided via --blender-version.
BLENDER_VERSION: str | None = ARGS.blender_version
if not BLENDER_VERSION:
    print(f"Existing Blender versions found: {', '.join(existing_versions)}")
    BLENDER_VERSION = input("Enter your Blender version: ").strip()

BLENDER_PATH = BLENDER_CONFIG_PATH / BLENDER_VERSION


BONSAI_PATH_CANDIDATES = (
    # Installed from Bonsai Unstable Repo.
    BLENDER_PATH / r"extensions/raw_githubusercontent_com/bonsai",
    # Installed via offline installation.
    BLENDER_PATH / r"extensions/user_default/bonsai",
    # Installed from Blender's official extensions platform.
    BLENDER_PATH / r"extensions/blender_org/bonsai",
)


# Determine BONSAI_PATH from existing options.
def find_bonsai_path() -> Path | None:
    for path in BONSAI_PATH_CANDIDATES:
        if path.exists():
            return path


# BONSAI_PATH: Path to 'bonsai' extension folder inside BLENDER_PATH.
# Typically resolved automatically, paths priority can be found in `find_bonsai_path`.
#
# Should be changed by user only if their installation path doesn't match any of the defaults
# or if they need different paths priority order.
BONSAI_PATH = find_bonsai_path()


binaries_source = ARGS.binaries_source
if binaries_source is None:
    print("Where do the compiled IfcOpenShell binaries (e.g. ifcopenshell_wrapper) come from?")
    for i, description in enumerate(BINARIES_SOURCE_DESCRIPTIONS.values(), start=1):
        print(f"{i}. {description}")
    choice = input("Enter 1 or 2: ").strip()
    binaries_source = list(BINARIES_SOURCE_DESCRIPTIONS)[int(choice) - 1]

should_copy_binaries = binaries_source == "installed"


# ---------------------------

# Never changed by user.
BLENDER_VERSION_INT = tuple(map(int, BLENDER_VERSION.split(".")))


# PACKAGE_PATH: Path to the site-packages of the Python bundled with Blender.
# Blender bundles a different Python per release (3.11 for 4.x, 3.13 for 5.1+), so read the
# version off the extensions folder instead of hardcoding a mapping that needs an edit
# every time Blender bumps it.
def find_package_path() -> Path:
    extensions_lib = BLENDER_PATH / "extensions/.local/lib"

    def version_key(path: Path) -> tuple[int, ...]:
        version = path.parent.name[len("python") :]
        try:
            return tuple(int(part) for part in version.split("."))
        except ValueError:
            # Unrecognized folder name, sort it below the versions we can parse.
            return (-1,)

    candidates = sorted(extensions_lib.glob("python*/site-packages"), key=version_key)
    if candidates:
        # Highest version wins in case an older Blender left a folder behind.
        return candidates[-1]

    # Fallback to the known mapping so the assert in `main` can report a sensible path.
    fallback_version = "3.13" if BLENDER_VERSION_INT >= (5, 1) else "3.11"
    return extensions_lib / f"python{fallback_version}/site-packages"


PACKAGE_PATH = find_package_path()


def main() -> None:
    REPO_PATH = Path(ARGS.repo_path) if ARGS.repo_path else None

    if REPO_PATH is None:
        script_path = Path(__file__)
        print(f"--repo-path is not set, deducing it from {script_path.name} location...")
        repo_bonsai_path = script_path.parent.parent
        assert repo_bonsai_path.name == "bonsai", (
            "Failed to deduce REPO_PATH from the script's location. "
            f"'{repo_bonsai_path}' is expected to be 'bonsai' folder."
        )
        REPO_PATH = repo_bonsai_path.parent.parent

    print("-" * 10)
    print("Script settings:")
    print("(all paths are confirmed to be existing)")
    print(f"REPO_PATH={REPO_PATH}")
    print(f"BLENDER_PATH={BLENDER_PATH}")
    print(f"BONSAI_PATH={BONSAI_PATH}")
    print(f"PACKAGE_PATH={PACKAGE_PATH}")
    print("-" * 10)

    assert REPO_PATH.exists(), f"Path '{REPO_PATH=!s}' doesn't exist, ensure --repo-path is set correctly."
    assert BLENDER_PATH.exists(), f"Path '{BLENDER_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert PACKAGE_PATH.exists(), f"Path '{PACKAGE_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert BONSAI_PATH is not None, (
        "Couldn't find BONSAI_PATH in any of the paths candidates. Example paths: {}".format(
            "\n".join(str(p) for p in BONSAI_PATH_CANDIDATES)
        )
    )

    input("Confirm the settings above and press Enter to continue or Ctrl-C to cancel...")

    # Handle symlinks
    # (they could be disabled by default on Windows).
    subprocess.check_call(("git", "config", "--local", "core.symlinks", "true"), cwd=REPO_PATH)
    symlinks_glob = "src/bonsai/bonsai/bim/data/templates/projects/*.ifc"
    # Delete and checkout is the only way to ensure files are added as symlinks.
    for path in REPO_PATH.glob(symlinks_glob):
        path.unlink()
    subprocess.check_call(("git", "checkout", "--", symlinks_glob), cwd=REPO_PATH)

    package_path = PACKAGE_PATH / "ifcopenshell"
    repo_package_path = REPO_PATH / "src" / "ifcopenshell-python" / "ifcopenshell"
    if not should_copy_binaries:
        assert any(repo_package_path.glob("_ifcopenshell_wrapper*")), (
            f"Couldn't find compiled ifcopenshell_wrapper in '{repo_package_path}'. "
            "Compile IfcOpenShell first or let the script copy the binaries from the installed Bonsai."
        )
    # There is nothing to copy if the package is already linked to the repo.
    elif not package_path.is_symlink():
        print("Copying compiled dependencies to the repo...")
        # Anything the installed package has on top of the tracked Python code is a binary.
        output = subprocess.check_output(("git", "ls-files"), cwd=repo_package_path, text=True)
        tracked = {line.split("/")[0] for line in output.splitlines()}
        for path in package_path.iterdir():
            if path.name in tracked or path.name == "__pycache__":
                continue
            dest = repo_package_path / path.name
            print(f"Copying {path} -> {dest}")
            # Never write through a symlink, as it may lead to binaries compiled locally.
            if dest.is_symlink():
                dest.unlink()
            shutil.copy(path, dest)

    print("Symlinking extension to the git repo...")
    # fmt: off
    symlinks = (
        (BONSAI_PATH / "__init__.py",  REPO_PATH / "src/bonsai/bonsai/__init__.py"),
        (PACKAGE_PATH / "bonsai",       REPO_PATH / "src/bonsai/bonsai"),
        (PACKAGE_PATH / "ifcopenshell", REPO_PATH / "src/ifcopenshell-python/ifcopenshell"),
        (PACKAGE_PATH / "ifccsv.py",    REPO_PATH / "src/ifccsv/ifccsv.py"),
        (PACKAGE_PATH / "ifcdiff.py",   REPO_PATH / "src/ifcdiff/ifcdiff.py"),
        (PACKAGE_PATH / "bsdd.py",      REPO_PATH / "src/bsdd/bsdd.py"),
        (PACKAGE_PATH / "bcf",          REPO_PATH / "src/bcf/bcf"),
        (PACKAGE_PATH / "ifc4d",        REPO_PATH / "src/ifc4d/ifc4d"),
        (PACKAGE_PATH / "ifc5d",        REPO_PATH / "src/ifc5d/ifc5d"),
        (PACKAGE_PATH / "ifccityjson",  REPO_PATH / "src/ifccityjson/ifccityjson"),
        (PACKAGE_PATH / "ifcclash",     REPO_PATH / "src/ifcclash/ifcclash"),
        (PACKAGE_PATH / "ifcpatch",     REPO_PATH / "src/ifcpatch/ifcpatch"),
        (PACKAGE_PATH / "ifctester",    REPO_PATH / "src/ifctester/ifctester"),
        (PACKAGE_PATH / "ifcfm",        REPO_PATH / "src/ifcfm/ifcfm"),
    )
    # fmt: on

    for path, dest in symlinks:
        print(f"Linking {path} -> {dest}.")
        # Check `is_symlink` first, as it could be a symlink to a directory or a broken symlink.
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        path.symlink_to(dest, dest.is_dir())

    print("Download third party dependencies...")
    BONSAI_DATA = PACKAGE_PATH / "bonsai" / "bim" / "data"
    downloads = (
        (
            "https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js",
            BONSAI_DATA / "gantt" / "jsgantt.js",
        ),
        (
            "https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css",
            BONSAI_DATA / "gantt" / "jsgantt.css",
        ),
        (
            "https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl",
            BONSAI_DATA / "brick" / "Brick.ttl",
        ),
        (
            "https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js",
            BONSAI_DATA / "webui" / "static" / "js" / "jquery.min.js",
        ),
    )

    for url, filepath in downloads:
        print(f"Downloading {url} -> {filepath}")
        urllib.request.urlretrieve(url, filepath)

    input("Dev environment is all set!! \nPress Enter to continue...")


if __name__ == "__main__":
    main()
