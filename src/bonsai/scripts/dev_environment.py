"""Setup Bonsai Development Environment.

Script links existing Bonsai installation to the provided IfcOpenShell repository.

If you're on Windows/Mac, using Blender 4.5, Bonsai is installed from unstable repo (raw_githubusercontent_com)
and this script is already part of IfcOpenShell repo you want to link, then you can just run it and it will just work.

Otherwise, see the SETTINGS section below to validate script settings to ensure it fits your evnironment.

Example usage:

    python /xxx/yyy/dev_environment.py
    python dev_environment.py

"""

import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Union

available_platforms = ("win32", "darwin", "linux")
if sys.platform not in available_platforms:
    print(f"Currently only available on {', '.join(available_platforms)}. Not available on {sys.platform}.")
    exit(1)

# ---------------------------
# SETTINGS.
# ---------------------------
# REPO_PATH: Path to your local IfcOpenShell repository.
# By default, this script will automatically detect the repository path based on its own location,
# so you usually do NOT need to set this manually.
# If you want to specify it explicitly, set it to the full absolute path, e.g.:
# > REPO_PATH = r"C:\Path\To\Your\IfcOpenShell\Repository"
REPO_PATH = r""

# BLENDER_PATH: Path to Blender's configuration folder.
# Usually don't need to change, just ensure Blender version matches.
BLENDER_VERSION = "4.5"

if sys.platform == "win32":
    BLENDER_PATH = Path.home() / f"AppData/Roaming/Blender Foundation/Blender/{BLENDER_VERSION}"
elif sys.platform == "darwin":
    BLENDER_PATH = Path.home() / f"Library/Application Support/Blender/{BLENDER_VERSION}"
elif sys.platform == "linux":
    BLENDER_PATH = Path.home() / f".config/blender/{BLENDER_VERSION}"
else:
    raise RuntimeError("Unsupported platform")


BONSAI_PATH_CANDIDATES = (
    # Installed from Bonsai Unstalble Repo.
    BLENDER_PATH / r"extensions/raw_githubusercontent_com/bonsai",
    # Installed via offline installation.
    BLENDER_PATH / r"extensions/user_default/bonsai",
    # Installed from Blender's official extensions platform.
    BLENDER_PATH / r"extensions/blender_org/bonsai",
)


# Determine BONSAI_PATH from existing options.
def find_bonsai_path() -> Union[Path, None]:
    for path in BONSAI_PATH_CANDIDATES:
        if path.exists():
            return path


# BONSAI_PATH: Path to 'bonsai' extension folder inside BLENDER_PATH.
# Typically resolved automatically, paths priority can be found in `find_bonsai_path`.
#
# Should be changed by user only if their installation path doesn't match any of the defaults
# or if they need different paths priority order.
BONSAI_PATH = find_bonsai_path()


# ---------------------------

# Never changed by user.
PACKAGE_PATH = BLENDER_PATH / r"extensions/.local/lib/python3.11/site-packages"


def main() -> None:
    global REPO_PATH

    if not REPO_PATH:
        script_path = Path(__file__)
        print(f"REPO_PATH is not set, deducing it from {script_path.name} location...")
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
    print("-" * 10)

    assert REPO_PATH.exists(), f"Path '{REPO_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert BLENDER_PATH.exists(), f"Path '{BLENDER_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert PACKAGE_PATH.exists(), f"Path '{PACKAGE_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert (
        BONSAI_PATH is not None
    ), "Couldn't find BONSAI_PATH in any of the paths candidates. Example paths: {}".format(
        "\n".join(str(p) for p in BONSAI_PATH_CANDIDATES)
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

    print("Copying compiled dependencies to the repo...")
    dest = REPO_PATH / "src" / "ifcopenshell-python" / "ifcopenshell"
    for path in PACKAGE_PATH.glob("ifcopenshell/*_wrapper*"):
        if path.suffix.lower() == ".pyi":
            continue
        dest_ = dest / path.name
        print(f"Copying {path} -> {dest_}")
        try:
            shutil.copy(path, dest_)
        except shutil.SameFileError:
            pass

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
        if path.is_dir():
            if path.is_symlink():
                path.unlink()
            else:
                shutil.rmtree(path)
        # Check `is_symlink` in case if it's a broken symlink.
        elif path.is_file() or path.is_symlink():
            path.unlink()
        else:
            pass
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

    input("Dev environment is all set. 🎉🎉\nPress Enter to continue..." "")


if __name__ == "__main__":
    main()
