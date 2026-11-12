#!/usr/bin/env python3
import argparse
import shlex
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

DIST_DIRS = (
    SCRIPT_DIR / "test/pyodide",
    SCRIPT_DIR / "test/pyodide-modular",
)
WHEEL_SRCS = (
    SCRIPT_DIR / "../dist",
    SCRIPT_DIR / "../dist-modular",
)


def run(cmd: list, **kwargs) -> None:
    print("$", shlex.join(str(part) for part in cmd))
    subprocess.check_call(cmd, **kwargs)


def setup() -> None:
    run(["uv", "pip", "install", "pytest-pyodide"])

    # Copy pyodide installation so we can modify it locally just for tests.
    pyodide_root = subprocess.check_output(["pyodide", "config", "get", "pyodide_root"], text=True).strip()
    pyodide_root_dist = Path(pyodide_root) / "dist"
    for dist_dir in DIST_DIRS:
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        shutil.copytree(pyodide_root_dist, dist_dir)


def run_tests() -> None:
    for dist_dir, wheel_src in zip(DIST_DIRS, WHEEL_SRCS):
        if not wheel_src.exists():
            raise RuntimeError(f"error: {wheel_src} does not exist")

        # Clean up previous wheels.
        for whl in dist_dir.glob("ifcopenshell*.whl"):
            whl.unlink()

        # Symlink new ones.
        for whl in wheel_src.glob("ifcopenshell*.whl"):
            (dist_dir / whl.name).symlink_to(whl.resolve())

    for dist_dir in DIST_DIRS:
        run(["pytest", f"--dist-dir={dist_dir}", "--capture=no"], cwd=SCRIPT_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["setup", "run"])
    args = parser.parse_args()

    if args.command == "setup":
        setup()
    else:
        run_tests()
