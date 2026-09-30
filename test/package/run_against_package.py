# /// script
# ///
"""Run the package tests against the built zips in the output directory.

The ifcopenshell-python zip with the lowest Python version is extracted into a
temporary directory that is put on PYTHONPATH, so the tests import the *packaged*
wrapper and plug-ins, not a source build. pytest is run through uv with the Python
version matching the zip.

Unless `--skip-bonsaiviewer` is passed, `BonsaiViewer --version` is run from the BonsaiViewer zip as well.
"""

import argparse
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
TEST_DEPENDENCIES = ("pytest", "typing_extensions", "numpy")
# Free-threaded builds (e.g. `ifcopenshell-python-313t-...`) are skipped.
ZIP_PATTERN = re.compile(r"ifcopenshell-python-(\d)(\d+)-.*\.zip")


def extract_preserving_symlinks(zip_path: Path, dest: Path) -> None:
    """`ZipFile.extractall` writes a symlink's target *text* as the file body, which turns
    the SONAME links of the Linux/macOS packages (`libTKernel.so.7.8 -> libTKernel.so.7.8.1`)
    into "file too short" load errors. Recreate them as links instead.
    It also drops file permissions, so restore them to keep executables runnable."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            target = dest / info.filename
            # Unix file type and permissions are stored in the high 16 bits.
            mode = info.external_attr >> 16
            is_symlink = stat.S_ISLNK(mode)
            if is_symlink:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(zf.read(info).decode())
            else:
                zf.extract(info, dest)
                # Permission bits (e.g. 0o755), 0 if the zip didn't store them.
                if permissions := stat.S_IMODE(mode):
                    target.chmod(permissions)


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


def run_python_tests(output_dir: Path, pytest_args: list[str]) -> int:
    zip_path, python_version = find_oldest_zip(output_dir)
    with tempfile.TemporaryDirectory(prefix="ifcopenshell-package-") as tmp:
        print(f"Extracting {zip_path} into {tmp}")
        extract_preserving_symlinks(zip_path, Path(tmp))
        env = dict(os.environ, PYTHONPATH=tmp, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        with_args = [arg for dep in TEST_DEPENDENCIES for arg in ("--with", dep)]
        # Run from the temp dir so a checked-out `src/ifcopenshell-python` can never shadow the package.
        cmd = [
            *("uv", "run", "--python", python_version, *with_args),
            *("python", "-m", "pytest", "-p", "no:cacheprovider", "-v", str(HERE), *pytest_args),
        ]
        print("$", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=tmp, env=env)
        return proc.returncode


def run_bonsaiviewer(output_dir: Path) -> int:
    """Run `BonsaiViewer --version` from the packaged zip to catch missing runtime libraries."""
    matches = sorted(output_dir.glob("BonsaiViewer-*.zip"))
    if len(matches) != 1:
        sys.exit(f"Expected exactly one BonsaiViewer zip in {str(output_dir)!r}, found: {matches}")
    zip_path = matches[0]
    with tempfile.TemporaryDirectory(prefix="bonsaiviewer-package-") as tmp:
        print(f"Extracting {zip_path} into {tmp}")
        extract_preserving_symlinks(zip_path, Path(tmp))
        executables = (
            "BonsaiViewer.app/Contents/MacOS/BonsaiViewer",
            "BonsaiViewer.exe",
            "BonsaiViewer",
        )
        exe = next((Path(tmp) / c for c in executables if (Path(tmp) / c).is_file()), None)
        if exe is None:
            sys.exit(f"No BonsaiViewer executable found in {zip_path}")
        cmd = [str(exe), "--version"]
        print("$", " ".join(cmd))
        return subprocess.run(cmd).returncode


class Args(NamedTuple):
    skip_bonsaiviewer: bool
    output_dir: Path
    pytest_args: list[str]


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-bonsaiviewer", action="store_true", help="Don't test the BonsaiViewer zip.")
    parser.add_argument("output_dir", type=Path, help="Directory with the packaged zips.")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="Extra arguments passed to pytest.")
    namespace = parser.parse_args()
    return Args(
        skip_bonsaiviewer=namespace.skip_bonsaiviewer,
        output_dir=namespace.output_dir,
        pytest_args=namespace.pytest_args,
    )


ARGS = parse_args()


def main() -> int:
    python_returncode = run_python_tests(ARGS.output_dir, ARGS.pytest_args)
    bonsaiviewer_returncode = 0 if ARGS.skip_bonsaiviewer else run_bonsaiviewer(ARGS.output_dir)
    return python_returncode or bonsaiviewer_returncode


if __name__ == "__main__":
    sys.exit(main())
