from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any


DEFAULT_CALLBACK_PORT = 8080


def config_root() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        root = Path(base) / "bonsaiviewer-autodesk"
    elif system == "Darwin":
        root = Path.home() / "Library" / "Application Support" / "bonsaiviewer-autodesk"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        root = Path(base) / "bonsaiviewer-autodesk"
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


def load_client_id() -> str:
    """The client id persisted in settings.json, or "" if none is set."""
    return str(_read().get("client_id", "")).strip()


def save_client_id(client_id: str) -> None:
    data = _read()
    data["client_id"] = client_id.strip()
    _write(data)


def stored_callback_port() -> int:
    value = _read().get("callback_port", DEFAULT_CALLBACK_PORT)
    try:
        port = int(value)
    except (TypeError, ValueError):
        return DEFAULT_CALLBACK_PORT
    return port if 1 <= port <= 65535 else DEFAULT_CALLBACK_PORT


def save_callback_port(port: int) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("Callback port must be between 1 and 65535.")
    data = _read()
    data["callback_port"] = port
    _write(data)
