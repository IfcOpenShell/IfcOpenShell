#!/usr/bin/env python3
"""Intended to be run after nix/build-all.py has finished the wasm build."""

import shutil
import subprocess
from pathlib import Path


def get_repo_root() -> Path:
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True)
    return Path(output.strip())


def run(cmd: list[str], **kwargs) -> None:
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, **kwargs)


def main() -> None:
    repo_root = get_repo_root()

    shutil.rmtree(repo_root / "dist", ignore_errors=True)
    shutil.rmtree(repo_root / "dist_modular", ignore_errors=True)
    run(["pyodide", "build"], cwd=repo_root)
    shutil.rmtree(repo_root / "ifcopenshell", ignore_errors=True)
    (repo_root / "setup.py").unlink(missing_ok=True)
    run(["git", "restore", "pyproject.toml"], cwd=repo_root)

    wheel = next((repo_root / "dist").glob("ifcopenshell-*.whl"))

    run(["uv", "run", "pyodide/order_pyodide_wheel_shared_objects.py", str(wheel)], cwd=repo_root)
    run(
        ["uv", "run", "pyodide/split_pyodide_ifcopenshell_wheel.py", str(wheel), "dist-modular/"],
        cwd=repo_root,
    )


if __name__ == "__main__":
    main()
