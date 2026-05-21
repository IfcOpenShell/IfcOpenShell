"""Tests for the RPC handlers (``bonsaiviewer_autodesk.connector``).

The non-interactive handlers are exercised against a fake ``ApsClient`` so no
network or GUI is touched; ``progress_dialog`` is stubbed out.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest

from bonsaiviewer_autodesk import cache, connector, settings
from bonsaiviewer_autodesk.rpc import RpcError


# --- fakes / fixtures --------------------------------------------------------


@contextmanager
def _fake_progress(_message):
    yield lambda *_args, **_kwargs: None


class FakeAps:
    """Stand-in for ApsClient covering only what the handlers call."""

    def __init__(self, *, item: dict | None = None, items: dict | None = None) -> None:
        self._item = item
        self._items = items or {}
        self.downloaded: list[tuple] = []
        self.uploaded: list[tuple] = []

    def get_item(self, _project_id: str, item_id: str) -> dict:
        if item_id in self._items:
            return dict(self._items[item_id])
        assert self._item is not None, f"no canned item for {item_id!r}"
        return dict(self._item)

    def download_storage_to_file(self, storage_id, destination_path, *, progress=None) -> None:
        Path(destination_path).write_bytes(b"<ifc data>")
        self.downloaded.append((storage_id, Path(destination_path)))

    def upload_file_to_folder(
        self, project_id, folder_id, local_path, *, display_name=None, progress=None
    ) -> dict:
        self.uploaded.append((project_id, folder_id, Path(local_path), display_name))
        return {
            "item_id": "uploaded-item",
            "version_id": "v1",
            "version_number": 1,
            "last_modified_time_utc": "2026-01-01T00:00:00Z",
            "last_modified_user_name": "Dion",
        }


@pytest.fixture
def make_connector(config_dir, cache_dir, monkeypatch):
    """Build an AutodeskConnector wired to a fake ApsClient."""
    monkeypatch.setattr(connector, "progress_dialog", _fake_progress)

    def _make(aps: FakeAps) -> connector.AutodeskConnector:
        conn = connector.AutodeskConnector()
        conn.aps = aps
        conn.auth = object()  # only identity matters to _require_aps
        return conn

    return _make


def _ifcfed_item(**overrides) -> dict:
    item = {
        "id": "item-1",
        "hidden": False,
        "storage_id": "urn:adsk.objects:os.object:bucket/object",
        "display_name": "Project.ifcfed",
        "version_id": "v1",
        "version_number": 1,
        "last_modified_time_utc": None,
        "last_modified_user_name": None,
        "parent_folder_id": "folder-1",
    }
    item.update(overrides)
    return item


# --- pure helpers ------------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, "0 B"),
        (512, "512 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (5 * 1024 * 1024, "5.0 MB"),
    ],
)
def test_format_bytes(value, expected):
    assert connector._format_bytes(value) == expected


def test_progress_detail_combines_percent_and_bytes():
    detail = connector._progress_detail(45, 4_500_000, 10_000_000)
    assert detail.startswith("45%, ")
    assert " / " in detail


def test_progress_detail_percent_only():
    assert connector._progress_detail(50, None, None) == "50%"


def test_progress_detail_bytes_without_total():
    assert connector._progress_detail(None, 2048, None) == "2.0 KB"


def test_progress_detail_empty_when_nothing_known():
    assert connector._progress_detail(None, None, None) == ""


def test_build_metadata_maps_all_fields():
    metadata = connector._build_metadata(
        {
            "version_number": 3,
            "last_modified_time_utc": "2026-01-01T00:00:00Z",
            "last_modified_user_name": "Dion",
        }
    )
    assert metadata == {
        "revision": "v3",
        "date": "2026-01-01T00:00:00Z",
        "author": "Dion",
    }


def test_build_metadata_omits_missing_fields():
    assert connector._build_metadata({}) == {}
    assert connector._build_metadata({"version_number": None}) == {}


def test_require_string_rejects_missing_or_blank():
    assert connector._require_string({"k": "v"}, "k") == "v"
    with pytest.raises(RpcError):
        connector._require_string({"k": "   "}, "k")
    with pytest.raises(RpcError):
        connector._require_string({}, "k")


def test_require_object_and_array_type_checks():
    assert connector._require_object({"a": 1}, "p") == {"a": 1}
    assert connector._require_array([1, 2], "p") == [1, 2]
    with pytest.raises(RpcError):
        connector._require_object([], "p")
    with pytest.raises(RpcError):
        connector._require_array({}, "p")


# --- credential wiring -------------------------------------------------------


def test_reload_credentials_without_client_id_leaves_aps_unset(config_dir):
    conn = connector.AutodeskConnector()
    assert conn.aps is None
    assert conn.auth is None
    with pytest.raises(RpcError, match="client id"):
        conn._require_aps()


def test_reload_credentials_with_client_id_builds_aps(config_dir):
    settings.save_client_id("my-client-id")
    conn = connector.AutodeskConnector()
    assert conn.aps is not None
    assert conn.auth is not None


# --- pull_ifcfed -------------------------------------------------------------


def test_pull_ifcfed_downloads_and_writes_manifest(make_connector):
    aps = FakeAps(item=_ifcfed_item())
    conn = make_connector(aps)

    result = conn.pull_ifcfed({"hub_id": "h", "project_id": "p", "item_id": "item-1"})

    path = Path(result["path"])
    assert path.exists()
    assert path.name == "Project.ifcfed"
    assert aps.downloaded  # the fake actually got asked to download

    manifest = cache.read_manifest(path)
    assert manifest["connector"] == "autodesk"
    assert manifest["item_id"] == "item-1"
    assert manifest["hub_id"] == "h"


def test_pull_ifcfed_rejects_non_ifcfed_file(make_connector):
    aps = FakeAps(item=_ifcfed_item(display_name="model.ifc"))
    conn = make_connector(aps)
    with pytest.raises(RpcError, match="ifcfed"):
        conn.pull_ifcfed({"hub_id": "h", "project_id": "p", "item_id": "item-1"})


def test_pull_ifcfed_rejects_deleted_item(make_connector):
    aps = FakeAps(item=_ifcfed_item(hidden=True))
    conn = make_connector(aps)
    with pytest.raises(RpcError, match="deleted"):
        conn.pull_ifcfed({"hub_id": "h", "project_id": "p", "item_id": "item-1"})


def test_pull_ifcfed_requires_string_fields(make_connector):
    conn = make_connector(FakeAps(item=_ifcfed_item()))
    with pytest.raises(RpcError, match="item_id"):
        conn.pull_ifcfed({"hub_id": "h", "project_id": "p"})


# --- pull_models -------------------------------------------------------------


def test_pull_models_skips_failures_with_none(make_connector):
    aps = FakeAps(
        items={
            "good": _ifcfed_item(id="good", display_name="good.ifc"),
            "gone": _ifcfed_item(id="gone", hidden=True),
        }
    )
    conn = make_connector(aps)
    models = [
        {"source": {"connector": "autodesk", "project_id": "p", "item_id": "good"}},
        {"source": {"connector": "autodesk", "project_id": "p", "item_id": "gone"}},
        {"source": {"connector": "other", "project_id": "p", "item_id": "good"}},
    ]

    results = conn.pull_models(models)

    assert len(results) == 3
    assert results[0] is not None and Path(results[0]["path"]).exists()
    assert results[1] is None  # hidden/deleted item
    assert results[2] is None  # wrong connector -> RpcError, swallowed


def test_pull_models_requires_a_json_array(make_connector):
    conn = make_connector(FakeAps(item=_ifcfed_item()))
    with pytest.raises(RpcError, match="array"):
        conn.pull_models({"not": "an array"})


# --- push_ifcfed -------------------------------------------------------------


def test_push_ifcfed_uploads_and_caches_with_manifest(make_connector, tmp_path):
    local = tmp_path / "local.ifcfed"
    local.write_bytes(b"ifcfed bytes")
    aps = FakeAps(item=_ifcfed_item())
    conn = make_connector(aps)

    result = conn.push_ifcfed(
        {
            "path": str(local),
            "manifest": {
                "connector": "autodesk",
                "hub_id": "h",
                "project_id": "p",
                "item_id": "item-1",
            },
        }
    )

    assert aps.uploaded
    cached = Path(result["path"])
    assert cached.exists()
    assert cache.read_manifest(cached)["item_id"] == "uploaded-item"


def test_push_ifcfed_rejects_missing_local_file(make_connector):
    conn = make_connector(FakeAps(item=_ifcfed_item()))
    with pytest.raises(RpcError, match="does not exist"):
        conn.push_ifcfed(
            {
                "path": "/no/such/file.ifcfed",
                "manifest": {
                    "connector": "autodesk",
                    "hub_id": "h",
                    "project_id": "p",
                    "item_id": "item-1",
                },
            }
        )


def test_push_ifcfed_rejects_non_ifcfed_extension(make_connector, tmp_path):
    local = tmp_path / "local.ifc"
    local.write_bytes(b"data")
    conn = make_connector(FakeAps(item=_ifcfed_item()))
    with pytest.raises(RpcError, match="ifcfed"):
        conn.push_ifcfed({"path": str(local), "manifest": {"connector": "autodesk"}})


def test_push_ifcfed_rejects_foreign_connector_manifest(make_connector, tmp_path):
    local = tmp_path / "local.ifcfed"
    local.write_bytes(b"data")
    conn = make_connector(FakeAps(item=_ifcfed_item()))
    with pytest.raises(RpcError, match="connector"):
        conn.push_ifcfed({"path": str(local), "manifest": {"connector": "other"}})
