#
# /// script
# # Latest Pyodide build env versions are listed here:
# # https://pyodide.github.io/pyodide/api/pyodide-cross-build-environments.json
# # https://github.com/pyodide/pyodide-build/blob/main/pyodide_build/xbuildenv_releases.py
# requires-python = "==3.13.2"
# dependencies = [
#   "requests",
#   "setuptools",
# ]
# ///
"""
Pack an IfcOpenShell WASM wheel using Pyodide build system.

Usage:
    uv run make_wheel.py           # Show this help
    uv run make_wheel.py --build   # Build wheel
    uv run make_wheel.py --clean   # Clean build artifacts and exit
"""

import argparse
import os
import re
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from urllib.parse import quote

import requests

# Get repo root (parent of this script's parent directory)
REPO_ROOT = Path(__file__).parent.parent
PYODIDE_DIR = REPO_ROOT / "pyodide"
BUILD_DIR = PYODIDE_DIR / "build"

# Hardcoded path (Windows packing workaround with --dev flag)
PYODIDE_BUILD = Path(r"L:\Projects\Github\pyodide-build")

# Wheel platform tag (from PYODIDE_EMSCRIPTEN_VERSION in pyodide-build/Makefile.envs)
WHEEL_PLATFORM_TAG = "emscripten_4_0_9_wasm32"

# Location where ifcopenshell will be extracted
IFCOPENSHELL_DIR = PYODIDE_DIR / "ifcopenshell"


class WheelBuilder:
    @staticmethod
    def extract_ifcopenshell_from_git(dst: Path) -> None:
        """Extract ifcopenshell directory from git repo into destination."""
        Tools.rmrf(dst)

        print(f"Extracting ifcopenshell from git to {dst}...")
        # Use git ls-files piped to git checkout-index to avoid copying
        # untracked or ignored files from the actual repo.
        ls_proc = subprocess.Popen(
            ["git", "ls-files", "-z", "src/ifcopenshell-python/ifcopenshell"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        checkout_proc = subprocess.Popen(
            ["git", "checkout-index", "-z", "--prefix", "pyodide/", "--stdin"],
            cwd=REPO_ROOT,
            stdin=ls_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert ls_proc.stdout is not None
        ls_proc.stdout.close()
        checkout_proc.communicate()

        if checkout_proc.returncode != 0:
            assert checkout_proc.stderr is not None
            raise RuntimeError(f"Failed to extract: {checkout_proc.stderr.decode()}")

        # Move src/ifcopenshell-python/ifcopenshell to ifcopenshell.
        temp_src = PYODIDE_DIR / "src" / "ifcopenshell-python" / "ifcopenshell"
        shutil.move(temp_src, dst)

        # Clean up temporary src directory.
        Tools.rmrf(PYODIDE_DIR / "src")

        print("✓ Extracted ifcopenshell from git")

    @staticmethod
    def get_wheel_url(makefile_path: Path) -> str:
        """Get S3 wheel URL based on BINARY_VERSION and BUILD_COMMIT from Makefile."""

        def parse_makefile_vars() -> dict[str, str]:
            content = makefile_path.read_text()
            vars: dict[str, str] = {}
            for match in re.finditer(r"^(BINARY_VERSION|BUILD_COMMIT):=(.+)$", content, re.MULTILINE):
                vars[match.group(1)] = match.group(2).strip()
            return vars

        vars: dict[str, str] = parse_makefile_vars()
        binary_version = vars["BINARY_VERSION"]
        build_commit = vars["BUILD_COMMIT"]
        filename = f"ifcopenshell-{binary_version}+{build_commit}-cp313-cp313-pyodide_2025_0_wasm32.whl"
        encoded_filename = quote(filename, safe="")
        return f"https://s3.amazonaws.com/ifcopenshell-builds/{encoded_filename}"

    @staticmethod
    def download_and_extract_so(url: str, build_dir: Path) -> tuple[Path, Path]:
        """Download wheel from URL and extract .so and .py files."""
        py_wrapper_filename = "ifcopenshell_wrapper.py"
        build_dir.mkdir(parents=True, exist_ok=True)

        wheel_path = build_dir / url.rsplit("/", 1)[-1]

        if wheel_path.exists():
            print(f"Using cached wheel: {wheel_path}")
        else:
            print(f"Downloading {url}...")
            response = requests.get(url)
            response.raise_for_status()
            wheel_path.write_bytes(response.content)

        print("Extracting _ifcopenshell_wrapper files...")
        with zipfile.ZipFile(wheel_path) as zf:
            so_files = [f for f in zf.namelist() if f.endswith(".so")]
            py_files = [f for f in zf.namelist() if f.endswith(py_wrapper_filename)]

            assert so_files, "No .so file found in wheel"
            assert py_files, f"No {py_wrapper_filename} file found in wheel"

            so_file = so_files[0]
            so_dst = build_dir / Path(so_file).name
            so_dst.write_bytes(zf.read(so_file))

            py_file = py_files[0]
            py_dst = build_dir / Path(py_file).name
            py_dst.write_bytes(zf.read(py_file))

        return so_dst, py_dst


class Tools:
    @staticmethod
    def run(
        cmd: list[str],
        cwd: Path | None = None,
    ) -> None:
        print(f"$ {' '.join(cmd)}")
        subprocess.check_call(cmd, cwd=cwd)

    @staticmethod
    def create_symlink(dst: Path, src: Path) -> None:
        Tools.rmrf(dst)
        dst.symlink_to(src)

    @staticmethod
    def rmrf(path: Path) -> None:
        if path.exists() or path.is_symlink():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()


def clean() -> None:
    """Remove build artifacts."""
    paths_to_remove = (
        BUILD_DIR,
        PYODIDE_DIR / ".pyodide_build",
        PYODIDE_DIR / "dist",
        PYODIDE_DIR / "ifcopenshell.egg-info",
        PYODIDE_DIR / "src",
        IFCOPENSHELL_DIR,
    )
    for path in paths_to_remove:
        if path.exists() or path.is_symlink():
            print(f"Removing {path}...")
            Tools.rmrf(path)
    print("✓ Clean complete")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--build", action="store_true", help="Build the wheel")
    parser.add_argument("--clean", action="store_true", help="Clean build folder")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Use editable pyodide-build from hardcoded path (Windows packing workaround)",
    )
    args = parser.parse_args()

    if not args.build and not args.clean:
        print(__doc__)
        return

    if args.clean:
        clean()
        return

    start_time = time.time()

    WheelBuilder.extract_ifcopenshell_from_git(IFCOPENSHELL_DIR)

    print("Downloading and extracting _ifcopenshell_wrapper files...")
    makefile = REPO_ROOT / "src" / "ifcopenshell-python" / "Makefile"
    wheel_url = WheelBuilder.get_wheel_url(makefile)
    so_file, py_file = WheelBuilder.download_and_extract_so(wheel_url, BUILD_DIR)

    Tools.create_symlink(IFCOPENSHELL_DIR / Path(so_file).name, so_file)
    Tools.create_symlink(IFCOPENSHELL_DIR / Path(py_file).name, py_file)

    print("Installing pyodide-build...")
    if args.dev:
        Tools.run(["uv", "pip", "install", "-e", str(PYODIDE_BUILD)])
    else:
        Tools.run(["uv", "pip", "install", "pyodide-build"])

    print("Building with pyodide...")
    # Use --no-isolation due to pyodide-build Windows support issues:
    # symlink_unisolated_packages fails with missing `_sysconfigdata_$(CPYTHON_ABI_FLAGS)_emscripten_wasm32-emscripten.py`.
    # Hardcode platform name since pyodide doesn't yet support overriding wheel tags on Windows.
    #
    # Use `LEGACY_PLATFORM` since pyodide 0.34.1 introduced new tag for wheels `pyemscripten`,
    # which doesn't work with pyodide itself yet - https://github.com/pyodide/pyodide/issues/6177.
    os.environ["USE_LEGACY_PLATFORM"] = "1"
    Tools.run(["pyodide", "build", f"-C--build-option=--plat-name={WHEEL_PLATFORM_TAG}"])

    elapsed = time.time() - start_time
    print(f"\n✓ Done! ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
