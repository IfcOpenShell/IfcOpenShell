"""Build the Autodesk connector bundle for the current OS.

Each OS builds on itself (PyInstaller does not cross-compile). The output is a
single zip ready to drop into the Bonsai Viewer connectors directory:

    dist/autodesk-<os>-<arch>.zip
      autodesk/
        connector.json
        bonsaiviewer-autodesk[.exe]
        _internal/...

Usage:

    pip install -e ".[build]"
    python packaging/build.py
"""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGING_DIR = PROJECT_ROOT / "packaging"
SPEC_FILE = PACKAGING_DIR / "bonsaiviewer-autodesk.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

CONNECTOR_FOLDER_NAME = "autodesk"
PYINSTALLER_OUTPUT_NAME = "bonsaiviewer-autodesk"


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


def _clean() -> None:
    for path in (DIST_DIR, BUILD_DIR):
        if path.exists():
            shutil.rmtree(path)


def _run_pyinstaller() -> Path:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            str(SPEC_FILE),
            "--noconfirm",
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(BUILD_DIR),
        ],
        cwd=PROJECT_ROOT,
    )
    produced = DIST_DIR / PYINSTALLER_OUTPUT_NAME
    if not produced.is_dir():
        raise SystemExit(f"PyInstaller did not produce expected folder: {produced}")
    return produced


def _assemble_connector_folder(pyinstaller_output: Path) -> Path:
    connector_dir = DIST_DIR / CONNECTOR_FOLDER_NAME
    if connector_dir.exists():
        shutil.rmtree(connector_dir)
    pyinstaller_output.rename(connector_dir)

    # The source-controlled connector.json uses the bare entry-point name so
    # `pip install -e .` works for development. For the bundled folder, the
    # binary lives next to connector.json, so rewrite `exec` to a relative path.
    manifest = json.loads((PROJECT_ROOT / "connector.json").read_text(encoding="utf-8"))
    binary_name = "bonsaiviewer-autodesk.exe" if platform.system() == "Windows" else "bonsaiviewer-autodesk"
    manifest["exec"] = f"./{binary_name}"
    (connector_dir / "connector.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return connector_dir


def _zip_connector_folder(tag: str) -> Path:
    archive_base = DIST_DIR / f"{CONNECTOR_FOLDER_NAME}-{tag}"
    return Path(shutil.make_archive(str(archive_base), "zip", DIST_DIR, CONNECTOR_FOLDER_NAME))


def main() -> int:
    tag = _platform_tag()
    print(f"Building Autodesk connector for {tag}")
    _clean()
    pyinstaller_output = _run_pyinstaller()
    connector_dir = _assemble_connector_folder(pyinstaller_output)
    archive = _zip_connector_folder(tag)
    print(f"Connector folder: {connector_dir}")
    print(f"Distribution zip: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
