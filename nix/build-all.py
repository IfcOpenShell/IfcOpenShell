#!/usr/bin/env python3
"""Compatibility entry point for building IfcOpenShell with Conan.

The dependency and CMake configuration live in the repository's conanfile.py.
This wrapper keeps the most commonly used build-all.py flags for local scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO_PATH = Path(__file__).resolve().parent.parent
CONAN = shutil.which("conan") or str(REPO_PATH / "aqt-env" / "bin" / "conan")


def is_enabled(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "on", "true", "yes"}


def materialize_package(version: str, shared: bool) -> None:
    listing = subprocess.check_output(
        [CONAN, "list", f"ifcopenshell/{version}:*", "-f", "json"],
        cwd=REPO_PATH,
        text=True,
    )
    data = json.loads(listing)["Local Cache"][f"ifcopenshell/{version}"]
    revision, revision_data = next(iter(data["revisions"].items()))
    package_id = next(iter(revision_data["packages"]))
    package_ref = f"ifcopenshell/{version}#{revision}:{package_id}"
    package_dir = Path(subprocess.check_output([CONAN, "cache", "path", package_ref], cwd=REPO_PATH, text=True).strip())

    arch = platform.machine()
    install_root = REPO_PATH / "build" / platform.system() / arch / "install"
    install_dir = install_root / "ifcopenshell"
    install_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_dir, install_dir, dirs_exist_ok=True)
    if shared:
        (install_root / "install_dirs.json").write_text("{}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="*", help="Legacy targets; Conan builds the configured package.")
    parser.add_argument("--build-examples", action="store_true")
    parser.add_argument("--build-bonsaiviewer", action="store_true")
    parser.add_argument("--diskcleanup", "-diskcleanup", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--lto", "-lto", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--shared", "-shared", action="store_true")
    parser.add_argument("--ifcopenshell-shared", "-ifcopenshell-shared", action="store_true")
    parser.add_argument("--occt-shared", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--mac-cross-compile-intel", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--wasm", action="store_true", help="WASM builds are not supported by this Conan recipe yet.")
    return parser.parse_known_args()[0]


def main() -> int:
    args = parse_args()
    if args.wasm:
        raise SystemExit("WASM builds are not supported by conanfile.py yet; use the Pyodide build workflow.")
    if not Path(CONAN).exists() and shutil.which(CONAN) is None:
        raise SystemExit("Conan was not found. Install it or activate the project's aqt-env environment.")

    options: dict[str, bool] = {
        "shared": args.shared or args.ifcopenshell_shared,
        "with_examples": args.build_examples,
        "build_bonsaiviewer": args.build_bonsaiviewer,
        "with_ifcpython": is_enabled(os.getenv("IFCOS_BUILD_PYTHON_WRAPPER"), True),
    }

    without = {target.removeprefix("--without-").lower() for target in sys.argv if target.startswith("--without-")}
    aliases = {
        "cgal": "with_cgal",
        "hdf5": "with_hdf5",
        "rocksdb": "with_rocksdb",
        "manifold": "with_manifold",
        "bonsaiviewer": "build_bonsaiviewer",
        "qt6": "build_bonsaiviewer",
    }
    for dependency, option in aliases.items():
        if dependency in without:
            options[option] = False

    schemas = os.getenv("IFCOS_SCHEMAS")
    version = (REPO_PATH / "VERSION").read_text().strip()
    build_type = os.getenv("BUILD_CFG", "RelWithDebInfo")
    command = [CONAN, "create", str(REPO_PATH), "--build=missing", "-s", f"build_type={build_type}"]
    for name, value in options.items():
        command.extend(["-o", f"{name}={value}"])
    if schemas:
        selected = {schema.strip() for schema in schemas.split(";")}
        for schema in ("2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"):
            command.extend(["-o", f"schema_{schema}={schema in selected}"])
    if args.verbose:
        command.append("-v")
    if args.lto:
        os.environ["CXXFLAGS"] = f'{os.environ.get("CXXFLAGS", "")} -flto'.strip()
        os.environ["CFLAGS"] = f'{os.environ.get("CFLAGS", "")} -flto'.strip()

    result = subprocess.run(command, cwd=REPO_PATH, check=False)
    if result.returncode == 0:
        materialize_package(version, options["shared"])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
