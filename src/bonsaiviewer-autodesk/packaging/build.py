"""Build the Autodesk connector bundle for the current OS.

Runs `cargo build --release` and packages the resulting binary +
connector.json into the same layout the old PyInstaller flow produced,
so build_viewer.sh and the CI workflows that already expected
`dist/autodesk/` and `dist/autodesk-<os>-<arch>.zip` keep working
unchanged:

    dist/autodesk-<os>-<arch>.zip
      autodesk/
        connector.json
        bonsaiviewer-autodesk[.exe]

The Rust binary statically links its deps, so unlike the PyInstaller
output there is no `_internal/` directory — single executable inside
the autodesk/ folder.

Usage:

    python packaging/build.py
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR     = PROJECT_ROOT / "dist"
TARGET_DIR   = PROJECT_ROOT / "target" / "release"

CONNECTOR_FOLDER_NAME = "autodesk"
BINARY_NAME           = "bonsaiviewer-autodesk"


def _platform_tag() -> str:
    system = platform.system()
    if system == "Darwin":
        os_name = "macos"
    elif system == "Windows":
        os_name = "windows"
    else:
        os_name = system.lower()

    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64"}:
        arch = "x86_64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine

    return f"{os_name}-{arch}"


def _binary_name_for_host() -> str:
    return f"{BINARY_NAME}.exe" if platform.system() == "Windows" else BINARY_NAME


def main() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    print("Running cargo build --release ...")
    subprocess.run(
        ["cargo", "build", "--release"],
        cwd=PROJECT_ROOT,
        check=True,
    )

    bin_src = TARGET_DIR / _binary_name_for_host()
    if not bin_src.exists():
        raise FileNotFoundError(
            f"cargo build did not produce expected binary at {bin_src}"
        )

    bundle_dir = DIST_DIR / CONNECTOR_FOLDER_NAME
    bundle_dir.mkdir(parents=True)
    shutil.copy(PROJECT_ROOT / "connector.json", bundle_dir / "connector.json")
    shutil.copy(bin_src, bundle_dir / _binary_name_for_host())

    zip_path = DIST_DIR / f"autodesk-{_platform_tag()}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(DIST_DIR))
    print(f"Wrote {zip_path}")
    print(f"      {bundle_dir}")


if __name__ == "__main__":
    main()
