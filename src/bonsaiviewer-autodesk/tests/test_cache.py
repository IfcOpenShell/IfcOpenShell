"""Tests for the on-disk cache layout (``bonsaiviewer_autodesk.cache``)."""

from __future__ import annotations

from bonsaiviewer_autodesk import cache


def test_cache_root_uses_xdg_on_linux(tmp_path, monkeypatch):
    monkeypatch.setattr(cache.platform, "system", lambda: "Linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    root = cache.cache_root()
    assert root == tmp_path / "xdg" / "bonsaiviewer-autodesk"
    assert root.is_dir()


def test_cache_root_uses_localappdata_on_windows(tmp_path, monkeypatch):
    monkeypatch.setattr(cache.platform, "system", lambda: "Windows")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
    root = cache.cache_root()
    assert root == tmp_path / "appdata" / "bonsaiviewer-autodesk" / "Cache"
    assert root.is_dir()


def test_cache_root_uses_library_caches_on_macos(tmp_path, monkeypatch):
    monkeypatch.setattr(cache.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(cache.Path, "home", lambda: tmp_path / "home")
    root = cache.cache_root()
    assert root == tmp_path / "home" / "Library" / "Caches" / "bonsaiviewer-autodesk"
    assert root.is_dir()


def test_ifcfed_dir_is_deterministic(cache_dir):
    first = cache.ifcfed_dir("project-1", "item-1")
    second = cache.ifcfed_dir("project-1", "item-1")
    assert first == second


def test_ifcfed_dir_varies_with_inputs(cache_dir):
    assert cache.ifcfed_dir("p", "item-1") != cache.ifcfed_dir("p", "item-2")
    assert cache.ifcfed_dir("p1", "item") != cache.ifcfed_dir("p2", "item")


def test_model_dir_is_per_version(cache_dir):
    v1 = cache.model_dir("p", "item", "v1")
    v2 = cache.model_dir("p", "item", "v2")
    assert v1 != v2
    assert cache.model_dir("p", "item", "v1") == v1


def test_prepare_sole_child_dir_wipes_existing_contents(cache_dir):
    directory = cache.ifcfed_dir("p", "item")
    directory.mkdir(parents=True)
    (directory / "stale.txt").write_text("old")

    result = cache.prepare_sole_child_dir(directory)

    assert result == directory
    assert directory.is_dir()
    assert list(directory.iterdir()) == []


def test_prepare_sole_child_dir_creates_when_absent(cache_dir):
    directory = cache.model_dir("p", "item", "v1")
    assert not directory.exists()
    cache.prepare_sole_child_dir(directory)
    assert directory.is_dir()


def test_manifest_round_trips(cache_dir):
    directory = cache.prepare_sole_child_dir(cache.ifcfed_dir("p", "item"))
    ifcfed_path = directory / "model.ifcfed"
    ifcfed_path.write_text("data")
    manifest = {"connector": "autodesk", "item_id": "item", "hub_id": "h"}

    manifest_path = cache.write_manifest(ifcfed_path, manifest)

    assert manifest_path.name == "model.ifcfed.manifest"
    assert cache.read_manifest(ifcfed_path) == manifest


def test_read_manifest_returns_none_when_absent(cache_dir):
    directory = cache.prepare_sole_child_dir(cache.ifcfed_dir("p", "item"))
    assert cache.read_manifest(directory / "model.ifcfed") is None
