"""Shared fixtures for the bonsaiviewer-autodesk test suite."""

from __future__ import annotations

import keyring
import keyring.backend
import keyring.errors
import pytest

from bonsaiviewer_autodesk import cache as cache_module
from bonsaiviewer_autodesk import settings as settings_module


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    """Redirect ``bonsaiviewer_autodesk.cache`` at an isolated tmp directory.

    Patches ``cache_root`` itself rather than ``XDG_CACHE_HOME`` so the
    redirect holds on every platform — on macOS/Windows ``cache_root`` ignores
    the XDG variables. Returns the directory ``cache_root()`` now resolves to.
    """
    root = tmp_path / "cache" / "bonsaiviewer-autodesk"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cache_module, "cache_root", lambda: root)
    return root


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    """Redirect ``bonsaiviewer_autodesk.settings`` at an isolated tmp directory.

    Patches ``config_root`` directly (platform-independent). Returns the
    directory ``config_root()`` now resolves to.
    """
    root = tmp_path / "config" / "bonsaiviewer-autodesk"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings_module, "config_root", lambda: root)
    return root


class InMemoryKeyring(keyring.backend.KeyringBackend):
    """A keyring backend that keeps secrets in a dict — never touches the OS."""

    priority = 1  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__()
        self._store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self._store.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self._store[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        try:
            del self._store[(service, username)]
        except KeyError as exc:
            raise keyring.errors.PasswordDeleteError("not found") from exc


@pytest.fixture
def memory_keyring():
    """Swap in the in-memory keyring backend for the duration of a test."""
    backend = InMemoryKeyring()
    previous = keyring.get_keyring()
    keyring.set_keyring(backend)
    try:
        yield backend
    finally:
        keyring.set_keyring(previous)
