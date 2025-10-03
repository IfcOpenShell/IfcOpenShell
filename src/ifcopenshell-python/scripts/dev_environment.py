"""Setup IfcOpenShell Development Environment.

Scripts creates symlinks in current user's site-packages to the IfcOpenShell repository.

Usage:
    python dev_environment.py
"""

import shutil
import site
from pathlib import Path

SITE = Path(site.getusersitepackages())
REPO_PATH = Path(__file__).parent.parent.parent.parent
REPO_PATH_SRC = REPO_PATH / "src"
assert REPO_PATH_SRC.exists(), f"'{REPO_PATH_SRC}' doesn't exist."

packages = {
    "ifcopenshell": REPO_PATH_SRC / "ifcopenshell-python" / "ifcopenshell",
    "ifcpatch": REPO_PATH_SRC / "ifcpatch" / "ifcpatch",
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
        # I guess it's a directory.
        shutil.rmtree(package_path)
    package_path.symlink_to(repo_package_path, True)
    print(f"Symlinking {package_path} -> {repo_package_path}")


PACKAGE_PATH = SITE / "ifcopenshell"
REPO_PACKAGE_PATH = REPO_PATH / "src" / "ifcopenshell-python" / "ifcopenshell"


print("Dev environment is all set! 🎉🎉")
