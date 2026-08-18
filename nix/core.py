#!/usr/bin/env python3
"""Shared utilities for WASM dependency building.

Used by both:
- nix/wasm_native.py (native C-ABI WASM build)
- nix/build-all.py (multi-platform build with -wasm flag)

Provides:
- run(): subprocess runner with logging
- sha256_file(), download_file(), extract_archive(): source handling
- apply_patch(), apply_patches_from_lock(): patching
- load_lockfile(), fetch_sources(), extract_source(): lockfile + source mgmt
- bootstrap_emsdk(), emsdk_env(), emsdk_binaries(): emsdk management
"""

import hashlib
import json
import logging
import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlretrieve

logger = logging.getLogger("wasm-core")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PATCHES_DIR = SCRIPT_DIR / "patches"
LOCK_FILE = SCRIPT_DIR / "sources.lock.json"


# ──────────────────────────────────────────────────────────────────────────────
# Subprocess / filesystem utilities
# ──────────────────────────────────────────────────────────────────────────────


def run(
    cmd: list[str],
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    """Run a subprocess command with logging.

    Merges `env` into the current environment. When `check` is True, a non-zero
    exit code raises `subprocess.CalledProcessError`. When `capture` is True,
    stdout/stderr are captured and returned on the CompletedProcess.
    """
    logger.info("$ %s", " ".join(str(c) for c in cmd))
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        check=check,
        capture_output=capture,
        text=True,
    )


def sha256_file(path: Path) -> str:
    """Compute the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path) -> None:
    """Download `url` to `dest` with a simple progress hook."""
    logger.info("Downloading %s -> %s", url, dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _reporthook(block_num: int, block_size: int, total_size: int) -> None:
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100.0, downloaded * 100.0 / total_size)
            mb = downloaded / (1 << 20)
            total_mb = total_size / (1 << 20)
            print(f"\r  {pct:5.1f}%  {mb:.1f}/{total_mb:.1f} MB", end="", flush=True)

    urlretrieve(url, str(dest), reporthook=_reporthook)
    print()  # newline after progress


def extract_archive(archive_path: Path, dest_dir: Path, archive_type: str) -> Path:
    """Extract an archive and return the top-level directory path.

    If the archive contains a single top-level directory, that path is returned.
    Otherwise `dest_dir` itself is returned.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Extracting %s -> %s", archive_path, dest_dir)

    if archive_type in ("tar.gz", "tar.bz2", "tar.xz", "tar"):
        with tarfile.open(str(archive_path), "r:*") as tf:
            members = tf.getmembers()
            top_dirs = set()
            for m in members:
                parts = m.name.split("/")
                if parts and parts[0]:
                    top_dirs.add(parts[0])
            tf.extractall(str(dest_dir), filter="data")
            if len(top_dirs) == 1:
                return dest_dir / top_dirs.pop()
            return dest_dir
    elif archive_type == "zip":
        with zipfile.ZipFile(str(archive_path), "r") as zf:
            zf.extractall(str(dest_dir))
            top_dirs = set()
            for name in zf.namelist():
                parts = name.split("/")
                if parts and parts[0]:
                    top_dirs.add(parts[0])
            if len(top_dirs) == 1:
                return dest_dir / top_dirs.pop()
            return dest_dir
    else:
        raise ValueError(f"Unsupported archive type: {archive_type}")


def apply_patch(patch_file: Path, target_dir: Path) -> None:
    """Apply a patch, accepting only a clean application or an already-applied patch."""
    logger.info("Applying patch %s in %s", patch_file, target_dir)
    command = ["patch", "-p1", "--forward", "-i", str(patch_file)]
    forward = run([*command, "--dry-run"], cwd=target_dir, check=False, capture=True)
    if forward.returncode == 0:
        run(command, cwd=target_dir)
        return
    reverse = run(
        ["patch", "-p1", "--reverse", "--dry-run", "-i", str(patch_file)],
        cwd=target_dir,
        check=False,
        capture=True,
    )
    if reverse.returncode == 0:
        logger.info("Patch already applied: %s", patch_file)
        return
    raise RuntimeError(
        f"Patch does not apply cleanly: {patch_file}\n{forward.stderr.strip()}"
    )


def build_jobs() -> int:
    raw = os.environ.get("WASM_NATIVE_JOBS")
    if raw is not None:
        try:
            jobs = int(raw)
        except ValueError as exc:
            raise ValueError("WASM_NATIVE_JOBS must be a positive integer") from exc
        if jobs < 1:
            raise ValueError("WASM_NATIVE_JOBS must be a positive integer")
        return jobs
    return min(8, max(1, os.cpu_count() or 1))


def which_or_error(name: str) -> str:
    """Return the full path to an executable, raising if it is not on PATH."""
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required tool not found: {name}")
    return path


# ──────────────────────────────────────────────────────────────────────────────
# Lockfile + sources
# ──────────────────────────────────────────────────────────────────────────────


def load_lockfile() -> dict[str, Any]:
    """Load and return the contents of `nix/sources.lock.json`."""
    with open(LOCK_FILE) as f:
        return json.load(f)


def fetch_sources(
    lock: dict[str, Any], deps: list[str], downloads_dir: Path
) -> dict[str, str]:
    """Download + hash-verify all archives for the given dep list.

    Git-based deps are skipped (they are cloned on demand by `extract_source`).
    Returns a mapping of dependency name to "ok" or "skipped (git)".
    """
    downloads_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}

    for dep_name in deps:
        if dep_name not in lock:
            raise KeyError(f"Dependency '{dep_name}' is missing from the lockfile")

        entry = lock[dep_name]
        url = entry["url"]
        version = entry["version"]
        archive_type = entry["archive_type"]
        expected_sha256 = entry.get("sha256")

        if archive_type == "git":
            logger.info("Skipping git-based dependency for fetch: %s", dep_name)
            results[dep_name] = "skipped (git)"
            continue

        filename = url.split("/")[-1]
        if not filename:
            filename = f"{dep_name}-{version}.{archive_type}"
        dest = downloads_dir / filename

        if dest.exists():
            logger.info("Already downloaded: %s", dest)
        else:
            download_file(url, dest)

        if expected_sha256:
            actual_sha256 = sha256_file(dest)
            if actual_sha256 != expected_sha256:
                raise RuntimeError(
                    f"SHA256 mismatch for {dep_name}: expected {expected_sha256}, "
                    f"got {actual_sha256}"
                )
            logger.info("SHA256 verified: %s", dep_name)
        else:
            raise ValueError(f"Archive dependency '{dep_name}' has no SHA256")

        results[dep_name] = "ok"

    return results


def extract_source(
    dep_name: str, lock: dict[str, Any], src_dir: Path, downloads_dir: Path
) -> Path:
    """Extract (or clone) the source for `dep_name` and return its path.

    For archive-based deps, the archive must already be in `downloads_dir`
    (i.e. `fetch_sources` must have been run). For git-based deps, the repo
    is cloned (depth=1, branch=ref) into `src_dir / dep_name`.
    """
    entry = lock[dep_name]
    if entry["archive_type"] == "git":
        return _clone_git_source(dep_name, entry, src_dir)

    url = entry["url"]
    filename = url.split("/")[-1]
    if not filename:
        filename = f"{dep_name}-{entry['version']}.{entry['archive_type']}"
    archive_path = downloads_dir / filename

    if not archive_path.exists():
        raise RuntimeError(f"Archive not found: {archive_path}. Run fetch first.")

    extract_dest = src_dir / dep_name
    if extract_dest.exists():
        logger.info("Source already extracted: %s", extract_dest)
        subdirs = [d for d in extract_dest.iterdir() if d.is_dir()]
        if len(subdirs) == 1:
            return subdirs[0]
        return extract_dest

    return extract_archive(archive_path, extract_dest, entry["archive_type"])


def _clone_git_source(dep_name: str, entry: dict[str, Any], src_dir: Path) -> Path:
    """Clone a git-based source (depth=1, branch=ref) into `src_dir / dep_name`."""
    target = src_dir / dep_name
    if target.exists():
        logger.info("Git source already cloned: %s", target)
        return target

    target.mkdir(parents=True, exist_ok=True)
    ref = entry.get("ref", entry.get("version"))
    logger.info("Cloning %s @ %s...", entry["url"], ref)
    run(["git", "clone", "--depth=1", "--branch", ref, entry["url"], str(target)])
    return target


def apply_patches_from_lock(
    dep_name: str, lock: dict[str, Any], src_dir: Path, patches_dir: Path
) -> None:
    """Apply all patches listed in the lockfile entry for `dep_name`.

    Patches are resolved relative to `patches_dir` (e.g. "occt/no_em_js.patch"
    becomes `patches_dir / "occt" / "no_em_js.patch"`). Missing patches are
    logged as a warning but do not raise.
    """
    entry = lock.get(dep_name, {})
    for patch_rel in entry.get("patches", []):
        patch_file = patches_dir / patch_rel
        if patch_file.exists():
            apply_patch(patch_file, src_dir)
        else:
            raise FileNotFoundError(f"Patch not found: {patch_file}")


# ──────────────────────────────────────────────────────────────────────────────
# emsdk management
# ──────────────────────────────────────────────────────────────────────────────


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
        raise RuntimeError(
            f"emsdk not found at {toolchain_dir}. Run bootstrap-toolchain first."
        )

    result = run(
        ["bash", "-c", f"source {emsdk_env_file} && env"],
        capture=True,
        check=True,
    )
    env_vars: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            env_vars[key] = value
    return env_vars


def emsdk_binaries(toolchain_dir: Path) -> dict[str, str]:
    """Return absolute paths to key emsdk binaries (emcc, emcmake, ...)."""
    emscripten = toolchain_dir / "upstream" / "emscripten"
    return {
        "emcc": str(emscripten / "emcc"),
        "em++": str(emscripten / "em++"),
        "emcmake": str(emscripten / "emcmake"),
        "emconfigure": str(emscripten / "emconfigure"),
        "emar": str(emscripten / "emar"),
        "emsdk": str(toolchain_dir / "emsdk"),
    }
