# /// script
# dependencies = [
#     "pytest",
#     "typing_extensions",
#     "numpy",
# ]
# ///
"""Run the package tests against a built ifcopenshell-python zip.

Usage: python run_against_package.py <zip or glob> [pytest args...]

The zip is extracted into a temporary directory that is put on PYTHONPATH, so the
tests import the *packaged* wrapper and plug-ins, not a source build. Runs with the
interpreter that runs this script, which therefore has to match the zip's Python
version and have pytest installed.
"""

import glob
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def extract_preserving_symlinks(zip_path: Path, dest: Path) -> None:
    """`ZipFile.extractall` writes a symlink's target *text* as the file body, which turns
    the SONAME links of the Linux/macOS packages (`libTKernel.so.7.8 -> libTKernel.so.7.8.1`)
    into "file too short" load errors. Recreate them as links instead."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            target = dest / info.filename
            is_symlink = (info.external_attr >> 16) & 0o170000 == 0o120000
            if is_symlink:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(zf.read(info).decode())
            else:
                zf.extract(info, dest)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    matches = sorted(glob.glob(sys.argv[1]))
    if len(matches) != 1:
        print(f"Expected exactly one zip for {sys.argv[1]!r}, found: {matches}")
        return 2
    zip_path = Path(matches[0])
    with tempfile.TemporaryDirectory(prefix="ifcopenshell-package-") as tmp:
        print(f"Extracting {zip_path} into {tmp}")
        extract_preserving_symlinks(zip_path, Path(tmp))
        env = dict(os.environ, PYTHONPATH=tmp, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        # Run from the temp dir so a checked-out `src/ifcopenshell-python` can never shadow the package.
        cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", str(HERE), *sys.argv[2:]]
        print("$", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=tmp, env=env)
        return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
