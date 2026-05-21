"""Tests for settings persistence (``bonsaiviewer_autodesk.settings``)."""

from __future__ import annotations

import json

import pytest

from bonsaiviewer_autodesk import settings


def _write_settings_json(config_dir, data: dict) -> None:
    (config_dir / "settings.json").write_text(json.dumps(data), encoding="utf-8")


def test_config_root_uses_xdg_on_linux(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.platform, "system", lambda: "Linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    root = settings.config_root()
    assert root == tmp_path / "xdg" / "bonsaiviewer-autodesk"
    assert root.is_dir()


def test_config_root_uses_appdata_on_windows(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.platform, "system", lambda: "Windows")
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    root = settings.config_root()
    assert root == tmp_path / "appdata" / "bonsaiviewer-autodesk"
    assert root.is_dir()


def test_config_root_uses_application_support_on_macos(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(settings.Path, "home", lambda: tmp_path / "home")
    root = settings.config_root()
    assert root == tmp_path / "home" / "Library" / "Application Support" / "bonsaiviewer-autodesk"
    assert root.is_dir()


def test_save_and_load_client_id_strips_whitespace(config_dir):
    settings.save_client_id("  abc123  ")
    assert settings.load_client_id() == "abc123"


def test_load_client_id_empty_when_nothing_configured(config_dir):
    assert settings.load_client_id() == ""


def test_callback_port_round_trips(config_dir):
    settings.save_callback_port(9001)
    assert settings.stored_callback_port() == 9001


def test_callback_port_defaults_when_unset(config_dir):
    assert settings.stored_callback_port() == settings.DEFAULT_CALLBACK_PORT


def test_callback_port_defaults_on_non_numeric_value(config_dir):
    _write_settings_json(config_dir, {"callback_port": "not-a-number"})
    assert settings.stored_callback_port() == settings.DEFAULT_CALLBACK_PORT


def test_callback_port_defaults_on_out_of_range_value(config_dir):
    _write_settings_json(config_dir, {"callback_port": 70000})
    assert settings.stored_callback_port() == settings.DEFAULT_CALLBACK_PORT


def test_save_callback_port_rejects_out_of_range(config_dir):
    with pytest.raises(ValueError):
        settings.save_callback_port(0)
    with pytest.raises(ValueError):
        settings.save_callback_port(70000)


def test_corrupt_settings_file_is_treated_as_empty(config_dir):
    (config_dir / "settings.json").write_text("{ not valid json", encoding="utf-8")
    assert settings.load_client_id() == ""
    assert settings.stored_callback_port() == settings.DEFAULT_CALLBACK_PORT


def test_save_client_id_preserves_other_keys(config_dir):
    settings.save_callback_port(9001)
    settings.save_client_id("abc")
    assert settings.stored_callback_port() == 9001
    assert settings.load_client_id() == "abc"
