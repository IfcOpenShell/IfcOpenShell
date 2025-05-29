"""Setup Bonsai Development Environment.

Script links existing Bonsai installation to the provided IfcOpenShell repository.

If you're on Windows, using Blender 4.4, Bonsai is installed from unstable repo (raw_githubusercontent_com)
and this script is already part of IfcOpenShell repo you want to link, then you can just run it and it will just work.

Otherwise, see the SETTINGS section below to validate script settings to ensure it fits your evnironment.

Example usage:

    python /xxx/yyy/dev_environment.py
    python dev_environment.py

"""

import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path

if sys.platform != "win32":
    print("Currently only available on Windows.")
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
BLENDER_PATH = Path.home() / r"AppData/Roaming/Blender Foundation/Blender/4.4"

# BONSAI_PATH: Path to 'bonsai' extension folder inside BLENDER_PATH.
# Need to ensure extensions repo folder in the path below ('raw_githubusercontent_com') matches yours.
#
# Typical scenarios:
# - Bonsai is installed from Bonsai Unstalble Repo - use 'raw_githubusercontent_com' (as it is by default)
# - Bonsai is installed via offline installation - use 'user_default'
# - Bonsai is installed from Blender's official extensions platform - use 'blender_org'
BONSAI_PATH = BLENDER_PATH / r"extensions/raw_githubusercontent_com/bonsai"

# ---------------------------

# Never changed by user.
PACKAGE_PATH = BLENDER_PATH / r"extensions/.local/lib/python3.11/site-packages"


def main():
    global REPO_PATH

    if not REPO_PATH:
        script_path = Path(__file__)
        print(f"REPO_PATH is not set, deducing it from {script_path.name} location...")
        repo_bonsai_path = script_path.parent.parent.parent
        assert repo_bonsai_path.name == "bonsai"
        REPO_PATH = repo_bonsai_path.parent.parent

    print("-" * 10)
    print("Script settings:")
    print(f"REPO_PATH={REPO_PATH}")
    print(f"BLENDER_PATH={BLENDER_PATH}")
    print(f"BONSAI_PATH={BONSAI_PATH}")
    print("-" * 10)

    assert REPO_PATH.exists(), f"Path '{REPO_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert BLENDER_PATH.exists(), f"Path '{BLENDER_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert PACKAGE_PATH.exists(), f"Path '{PACKAGE_PATH=!s}' doesn't exist, ensure variable is set correctly."
    assert BONSAI_PATH.exists(), f"Path '{BONSAI_PATH=!s}' doesn't exist, ensure variable is set correctly."

    input("Confirm the settings above and press Enter to continue or Ctrl-C to cancel...")

    # Handle symlinks
    # (they could be disabled by default on Windows).
    subprocess.run("git config --local core.symlinks true", cwd=REPO_PATH)
    symlinks_glob = "src/bonsai/bonsai/bim/data/templates/projects/*.ifc"
    # Delete and checkout is the only way to ensure files are added as symlinks.
    for path in REPO_PATH.glob(symlinks_glob):
        path.unlink()
    subprocess.run((f"git checkout -- {symlinks_glob}"), cwd=REPO_PATH)

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
        elif path.is_file():
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
