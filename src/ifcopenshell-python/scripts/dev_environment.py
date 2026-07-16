#!/usr/bin/env python3
"""Setup IfcOpenShell Development Environment.

Scripts creates symlinks in current user's site-packages to the IfcOpenShell repository.

Usage:
    python dev_environment.py
"""

import shutil
import site
from pathlib import Path

SITE = Path(site.getusersitepackages())
SITE.mkdir(parents=True, exist_ok=True)
REPO_PATH = Path(__file__).parent.parent.parent.parent
REPO_PATH_SRC = REPO_PATH / "src"
assert REPO_PATH_SRC.exists(), f"'{REPO_PATH_SRC}' doesn't exist."

packages = {
    "bcf": REPO_PATH_SRC / "bcf" / "bcf",
    "bsdd.py": REPO_PATH_SRC / "bsdd" / "bsdd.py",
    "ifc4d": REPO_PATH_SRC / "ifc4d" / "ifc4d",
    "ifc5d": REPO_PATH_SRC / "ifc5d" / "ifc5d",
    "ifccityjson": REPO_PATH_SRC / "ifccityjson" / "ifccityjson",
    "ifcclash": REPO_PATH_SRC / "ifcclash" / "ifcclash",
    "ifccsv.py": REPO_PATH_SRC / "ifccsv" / "ifccsv.py",
    "ifcdiff.py": REPO_PATH_SRC / "ifcdiff" / "ifcdiff.py",
    "ifcfm": REPO_PATH_SRC / "ifcfm" / "ifcfm",
    "ifcopenshell": REPO_PATH_SRC / "ifcopenshell-python" / "ifcopenshell",
    "ifcpatch": REPO_PATH_SRC / "ifcpatch" / "ifcpatch",
    "ifctester": REPO_PATH_SRC / "ifctester" / "ifctester",
}


print(f"Repository path: '{REPO_PATH}'.")
print(f"site-packages path: '{SITE}'.")
input("Confirm the settings above and press Enter to continue or Ctrl-C to cancel...")


for package, repo_package_path in packages.items():
    package_path = SITE / package
    if package_path.is_symlink():
        if package_path.resolve() == repo_package_path:
            print(f"'{package}' is already linked to the repository, no action needed.")
            continue
        package_path.unlink()
    if package_path.exists():
        if package_path.is_dir():
            shutil.rmtree(package_path)
        else:
            package_path.unlink()
    print(f"Symlinking {package_path} -> {repo_package_path}")
    package_path.symlink_to(repo_package_path, target_is_directory=repo_package_path.is_dir())


PACKAGE_PATH = SITE / "ifcopenshell"
REPO_PACKAGE_PATH = REPO_PATH / "src" / "ifcopenshell-python" / "ifcopenshell"


print("Dev environment is all set! 🎉🎉")
