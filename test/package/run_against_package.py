# /// script
# # Python 3.12 is needed for reliable `platform.machine()` on arm, see win/build-all-win.py.
# requires-python = ">=3.12"
# ///
"""Run the package tests against the built zips in the output directory.

The ifcopenshell-python zip with the lowest Python version is extracted into a
temporary directory that is put on PYTHONPATH, so the tests import the *packaged*
wrapper and plug-ins, not a source build. pytest is run through uv with the Python
version matching the zip.

Unless `--skip-bonsaiviewer` is passed, the BonsaiViewer zip is extracted as well: its path is passed
to the tests in `IFCOPENSHELL_PACKAGE_TESTS_BONSAIVIEWER` and `BonsaiViewer --version` is run.
"""

import argparse
import os
import platform
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


def run_python_tests(output_dir: Path, pytest_args: list[str], bonsaiviewer: Path | None) -> int:
    zip_path, python_version = find_oldest_zip(output_dir)
    python_request = python_version
    if sys.platform == "win32" and platform.machine() == "ARM64":
        # On Windows ARM64 uv defaults to x86_64 Python, which can't load an ARM64 .pyd.
        # See https://github.com/astral-sh/uv/issues/12906
        python_request = f"{python_version}-aarch64"
    with tempfile.TemporaryDirectory(prefix="ifcopenshell-package-") as tmp:
        print(f"Extracting {zip_path} into {tmp}")
        extract_preserving_symlinks(zip_path, Path(tmp))
        env = dict(os.environ, PYTHONPATH=tmp, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        if bonsaiviewer:
            env["IFCOPENSHELL_PACKAGE_TESTS_BONSAIVIEWER"] = str(bonsaiviewer)
        with_args = [arg for dep in TEST_DEPENDENCIES for arg in ("--with", dep)]
        # Run from the temp dir so a checked-out `src/ifcopenshell-python` can never shadow the package.
        cmd = [
            *("uv", "run", "--python", python_request, *with_args),
            *("python", "-m", "pytest", "-p", "no:cacheprovider", "-v", str(HERE), *pytest_args),
        ]
        print("$", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=tmp, env=env)
        return proc.returncode


def run_bonsaiviewer(exe: Path | str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run BonsaiViewer with `args` and print its output."""
    cmd = [str(exe), *args]
    print("$", " ".join(cmd))
    env = dict(os.environ)
    if sys.platform.startswith("linux"):
        # TODO: in theory `BonsaiViewer` should be runnable as cli too?
        # No display on CI, and the default xcb platform plugin needs one (and libxcb-cursor0).
        env["QT_QPA_PLATFORM"] = "offscreen"
    # `capture_output` is attaching stdio.
    # `--version` without stdio shows a message box and leaves the process hanging.
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(proc.stdout + proc.stderr, end="")
    return proc


def extract_bonsaiviewer(output_dir: Path, dest: Path) -> Path:
    """Extract the BonsaiViewer zip into `dest` and return the path to the executable."""
    matches = sorted(output_dir.glob("BonsaiViewer-*.zip"))
    if len(matches) != 1:
        sys.exit(f"Expected exactly one BonsaiViewer zip in {str(output_dir)!r}, found: {matches}")
    zip_path = matches[0]
    print(f"Extracting {zip_path} into {dest}")
    extract_preserving_symlinks(zip_path, dest)
    executables = (
        "BonsaiViewer.app/Contents/MacOS/BonsaiViewer",
        "BonsaiViewer.exe",
        "BonsaiViewer",
    )
    exe = next((dest / c for c in executables if (dest / c).is_file()), None)
    if exe is None:
        sys.exit(f"No BonsaiViewer executable found in {zip_path}")
    return exe


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


def main() -> int:
    args = parse_args()
    if args.skip_bonsaiviewer:
        return run_python_tests(args.output_dir, args.pytest_args, None)
    with tempfile.TemporaryDirectory(prefix="bonsaiviewer-package-") as tmp:
        exe = extract_bonsaiviewer(args.output_dir, Path(tmp))
        python_returncode = run_python_tests(args.output_dir, args.pytest_args, exe)
        # Catch missing runtime libraries.
        bonsaiviewer_returncode = run_bonsaiviewer(exe, "--version").returncode
        # Just for the log, the result is checked by the tests.
        run_bonsaiviewer(exe, "--list-plugins")
    return python_returncode or bonsaiviewer_returncode


if __name__ == "__main__":
    sys.exit(main())
