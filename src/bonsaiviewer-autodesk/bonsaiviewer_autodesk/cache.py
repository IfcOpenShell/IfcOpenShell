from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from pathlib import Path
from typing import Any


def cache_root() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        root = Path(base) / "bonsaiviewer-autodesk" / "Cache"
    elif system == "Darwin":
        root = Path.home() / "Library" / "Caches" / "bonsaiviewer-autodesk"
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
        root = Path(base) / "bonsaiviewer-autodesk"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _short_hash(*parts: str) -> str:
    joined = "\x1f".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def ifcfed_dir(project_id: str, item_id: str) -> Path:
    """Stable directory for an .ifcfed. Re-downloads overwrite in place so the
    viewer's open path remains valid across sync operations."""
    return cache_root() / "ifcfeds" / _short_hash(project_id, item_id)


def model_dir(project_id: str, item_id: str, version_id: str) -> Path:
    """Per-version directory for a model. A new resolved version → a new
    directory, satisfying the spec's invariant that sidecars regenerate when
    the model file changes."""
    return cache_root() / "models" / _short_hash(project_id, item_id, version_id)


def prepare_sole_child_dir(directory: Path) -> Path:
    """Clear the directory so the file we write is the only child."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_manifest(ifcfed_path: Path, manifest: dict[str, Any]) -> Path:
    manifest_path = ifcfed_path.with_name(ifcfed_path.name + ".manifest")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def read_manifest(ifcfed_path: Path) -> dict[str, Any] | None:
    manifest_path = ifcfed_path.with_name(ifcfed_path.name + ".manifest")
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))
