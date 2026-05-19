from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any


def config_root() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        root = Path(base) / "ifcviewer-autodesk"
    elif system == "Darwin":
        root = Path.home() / "Library" / "Application Support" / "ifcviewer-autodesk"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        root = Path(base) / "ifcviewer-autodesk"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _settings_path() -> Path:
    return config_root() / "settings.json"


def _read() -> dict[str, Any]:
    path = _settings_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write(data: dict[str, Any]) -> None:
    _settings_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def stored_client_id() -> str:
    """Whatever is persisted in settings.json — ignores the env var."""
    return str(_read().get("client_id", "")).strip()


def env_client_id() -> str:
    """Whatever APS_CLIENT_ID currently has — ignores settings.json."""
    return os.environ.get("APS_CLIENT_ID", "").strip()


def load_client_id() -> str:
    """The effective value: env var wins, so dev overrides keep working."""
    return env_client_id() or stored_client_id()


def save_client_id(client_id: str) -> None:
    data = _read()
    data["client_id"] = client_id.strip()
    _write(data)
