# /// script
# ///
"""Run the package tests against a built ifcopenshell-python zip.

The zip with the lowest Python version is picked from the output directory and
extracted into a temporary directory that is put on PYTHONPATH, so the tests import
the *packaged* wrapper and plug-ins, not a source build. pytest is run through uv with
the Python version matching the zip.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_DEPENDENCIES = ("pytest", "typing_extensions", "numpy")
# Free-threaded builds (e.g. `ifcopenshell-python-313t-...`) are skipped.
ZIP_PATTERN = re.compile(r"ifcopenshell-python-(\d)(\d+)-.*\.zip")


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


def find_oldest_zip(output_dir: Path) -> tuple[Path, str]:
    """Return the zip with the lowest Python version and that version (e.g. "3.13")."""
    zips: defaultdict[tuple[int, int], list[Path]] = defaultdict(list)
    for path in output_dir.iterdir():
        if match := ZIP_PATTERN.fullmatch(path.name):
            zips[(int(match[1]), int(match[2]))].append(path)
    if not zips:
        sys.exit(f"No ifcopenshell-python zips found in {str(output_dir)!r}")
    version = min(zips)
    if len(zips[version]) != 1:
        sys.exit(f"Expected exactly one zip for Python {version}, found: {sorted(zips[version])}")
    return zips[version][0], ".".join(map(str, version))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", type=Path, help="Directory with the packaged ifcopenshell-python zips.")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="Extra arguments passed to pytest.")
    args = parser.parse_args()

    zip_path, python_version = find_oldest_zip(args.output_dir)
    with tempfile.TemporaryDirectory(prefix="ifcopenshell-package-") as tmp:
        print(f"Extracting {zip_path} into {tmp}")
        extract_preserving_symlinks(zip_path, Path(tmp))
        env = dict(os.environ, PYTHONPATH=tmp, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        with_args = [arg for dep in TEST_DEPENDENCIES for arg in ("--with", dep)]
        # Run from the temp dir so a checked-out `src/ifcopenshell-python` can never shadow the package.
        cmd = [
            *("uv", "run", "--python", python_version, *with_args),
            *("python", "-m", "pytest", "-p", "no:cacheprovider", "-v", str(HERE), *args.pytest_args),
        ]
        print("$", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=tmp, env=env)
        return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
