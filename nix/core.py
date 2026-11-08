#!/usr/bin/env python3
"""Shared utilities for the standalone WASM build.

Used by `nix/build-all.py --native-wasm`, where the pinned emsdk replaces the
pyodide build environment. Pinned toolchain versions live in
`nix/sources.lock.json`.

Provides:
- run(): subprocess runner with logging
- load_lockfile(): pinned versions and source locations
- bootstrap_emsdk(), emsdk_env(): emsdk management
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("wasm-core")

SCRIPT_DIR = Path(__file__).resolve().parent
LOCK_FILE = SCRIPT_DIR / "sources.lock.json"


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess command with logging.

    When `capture` is True, stdout/stderr are captured and returned on the
    CompletedProcess. A non-zero exit code raises `subprocess.CalledProcessError`.
    """
    logger.info("$ %s", " ".join(str(c) for c in cmd))
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=capture,
        text=True,
    )


def load_lockfile() -> dict[str, Any]:
    """Load and return the contents of `nix/sources.lock.json`."""
    with open(LOCK_FILE) as f:
        return json.load(f)


# ------------------------------------------------------------------------------
# emsdk management
# ------------------------------------------------------------------------------


def bootstrap_emsdk(lock: dict[str, Any], target_dir: Path, force: bool = False) -> int:
    """Install the pinned emsdk into `target_dir`.

    If `target_dir` already contains an activated emsdk, the install is
    skipped unless `force=True`.
    """
    emsdk_entry = lock["emsdk"]
    version = emsdk_entry["version"]

    if target_dir.exists() and (target_dir / "emsdk_env.sh").exists():
        logger.info("emsdk already installed at %s", target_dir)
        if not force:
            logger.info("Use force=True to reinstall.")
            return 0
        logger.info("Force reinstalling emsdk...")
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Cloning emsdk %s...", version)
    run(
        [
            "git",
            "clone",
            "--depth=1",
            "--branch",
            version,
            emsdk_entry["url"],
            str(target_dir),
        ]
    )

    logger.info("Installing emsdk %s...", version)
    run([str(target_dir / "emsdk"), "install", version], cwd=target_dir)

    logger.info("Activating emsdk %s...", version)
    run([str(target_dir / "emsdk"), "activate", version], cwd=target_dir)

    logger.info("emsdk %s installed at %s", version, target_dir)
    return 0


def emsdk_env(toolchain_dir: Path) -> dict[str, str]:
    """Return environment variables produced by sourcing `emsdk_env.sh`.

    Raises `RuntimeError` if emsdk is not installed at `toolchain_dir`.
    """
    emsdk_env_file = toolchain_dir / "emsdk_env.sh"
    if not emsdk_env_file.exists():
        raise RuntimeError(f"emsdk not found at {toolchain_dir}. Run bootstrap first.")

    result = run(
        ["bash", "-c", f"source {emsdk_env_file} && env"],
        capture=True,
    )
    env_vars: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            env_vars[key] = value
    return env_vars
