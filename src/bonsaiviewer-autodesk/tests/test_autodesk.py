"""Tests for the Autodesk auth + APS client (``bonsaiviewer_autodesk.autodesk``).

HTTP is mocked through the injectable ``transport`` seam using
``httpx.MockTransport``; time through the injectable ``now`` clock; and the
OAuth redirect through the injectable ``callback_waiter``.
"""

from __future__ import annotations

import datetime as dt
import socket
import threading
import time
from collections import deque

import httpx
import keyring.errors
import pytest

from bonsaiviewer_autodesk import autodesk
from bonsaiviewer_autodesk.rpc import RpcError


# --- HTTP routing ------------------------------------------------------------


def _build_response(spec: dict) -> httpx.Response:
    kwargs = {key: spec[key] for key in ("json", "text", "content", "headers") if key in spec}
    return httpx.Response(spec.get("status", 200), **kwargs)


class Router:
    """A tiny httpx.MockTransport router.

    Routes match on HTTP method plus a substring of the request URL, in
    declaration order. Pass multiple specs to a route to return them in turn
    (the last one repeats); every request is recorded on ``requests``.
    """

    def __init__(self) -> None:
        self._routes: list[tuple[str, str, deque]] = []
        self.requests: list[httpx.Request] = []

    def add(self, method: str, contains: str, *specs: dict) -> "Router":
        self._routes.append((method, contains, deque(specs or ({},))))
        return self

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        for method, contains, specs in self._routes:
            if request.method == method and contains in str(request.url):
                spec = specs[0] if len(specs) == 1 else specs.popleft()
                return _build_response(spec)
        return httpx.Response(404, text=f"unrouted {request.method} {request.url}")

    @property
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self._handle)

    def count(self, method: str, contains: str) -> int:
        return sum(
            1 for r in self.requests if r.method == method and contains in str(r.url)
        )


# --- fakes -------------------------------------------------------------------


class FakeTokenStore:
    """In-memory stand-in for KeyringTokenStore."""

    def __init__(self, initial: dict | None = None) -> None:
        self.value = initial

    def load(self) -> dict | None:
        return self.value

    def save(self, value: dict) -> None:
        self.value = value

    def delete(self) -> None:
        self.value = None


class FakeAuth:
    """Minimal AuthSessionService stand-in for ApsClient tests."""

    def ensure_access_token(self) -> str:
        return "fake-token"


FIXED_NOW = dt.datetime(2026, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)


def iso(offset_seconds: int) -> str:
    return (FIXED_NOW + dt.timedelta(seconds=offset_seconds)).isoformat()


def stored_token_dict(*, access_offset: int, refresh_offset: int) -> dict:
    return {
        "client_id": "cid",
        "access_token": "current-access",
        "refresh_token": "current-refresh",
        "access_token_expires_at_utc": iso(access_offset),
        "refresh_token_expires_at_utc": iso(refresh_offset),
        "scope": "data:read",
    }


def make_auth(
    *,
    router: Router | None = None,
    token_store: FakeTokenStore | None = None,
    callback_waiter=None,
    callback_url: str = "http://localhost:8080/",
) -> autodesk.AuthSessionService:
    return autodesk.AuthSessionService(
        client_id="cid",
        callback_url=callback_url,
        scope="data:read",
        token_store=token_store or FakeTokenStore(),
        transport=(router or Router()).transport,
        now=lambda: FIXED_NOW,
        callback_waiter=callback_waiter,
    )


def make_client(router: Router) -> autodesk.ApsClient:
    return autodesk.ApsClient(FakeAuth(), transport=router.transport)


# --- pure helpers ------------------------------------------------------------


def test_base64url_strips_padding():
    assert autodesk._base64url(b"\x00") == "AA"
    assert "=" not in autodesk._base64url(b"\x00\x00")


def test_generate_code_verifier_is_url_safe_and_unique():
    verifier = autodesk.generate_code_verifier()
    assert not set(verifier) & set("=+/")
    assert autodesk.generate_code_verifier() != autodesk.generate_code_verifier()


def test_generate_code_challenge_matches_rfc7636_vector():
    # RFC 7636 Appendix B test vector.
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    assert (
        autodesk.generate_code_challenge(verifier)
        == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    )


def test_parse_storage_id_splits_bucket_and_object():
    bucket, obj = autodesk.ApsClient._parse_storage_id(
        "urn:adsk.objects:os.object:wip.dm.prod/abc-123.ifc"
    )
    assert bucket == "wip.dm.prod"
    assert obj == "abc-123.ifc"


@pytest.mark.parametrize(
    "bad",
    [
        "not-a-urn",
        "urn:adsk.objects:os.object:bucketonly",
        "urn:adsk.objects:os.object:/object",
        "urn:adsk.objects:os.object:bucket/",
    ],
)
def test_parse_storage_id_rejects_malformed(bad):
    with pytest.raises(RpcError):
        autodesk.ApsClient._parse_storage_id(bad)


def test_entry_extracts_fields():
    item = {
        "id": "x",
        "type": "items",
        "attributes": {
            "displayName": "Model.ifc",
            "extension": {"type": "items:autodesk.bim360:File"},
        },
    }
    assert autodesk.ApsClient._entry(item) == {
        "id": "x",
        "type": "items",
        "display_name": "Model.ifc",
        "name": None,
        "extension_type": "items:autodesk.bim360:File",
    }


def test_relationship_id_handles_dict_list_and_missing():
    data = {
        "relationships": {
            "parent": {"data": {"id": "p1"}},
            "files": {"data": [{"id": "f1"}, {"id": "f2"}]},
        }
    }
    assert autodesk.ApsClient._relationship_id(data, "parent") == "p1"
    assert autodesk.ApsClient._relationship_id(data, "files") == "f1"
    assert autodesk.ApsClient._relationship_id(data, "missing") is None


def test_entry_name_matches_is_case_insensitive():
    assert autodesk.ApsClient._entry_name_matches({"display_name": "Model.IFC"}, "model.ifc")
    assert autodesk.ApsClient._entry_name_matches({"name": "Model.IFC"}, "model.ifc")
    assert not autodesk.ApsClient._entry_name_matches({"display_name": "other.ifc"}, "model.ifc")


# --- KeyringTokenStore -------------------------------------------------------


def test_keyring_token_store_round_trip(memory_keyring):
    store = autodesk.KeyringTokenStore(service_name="svc", username="user")
    assert store.load() is None
    store.save({"access_token": "abc"})
    assert store.load() == {"access_token": "abc"}
    store.delete()
    assert store.load() is None


def test_keyring_token_store_delete_missing_is_noop(memory_keyring):
    store = autodesk.KeyringTokenStore(service_name="svc", username="user")
    store.delete()  # no entry to delete — must not raise


def test_keyring_missing_backend_surfaces_friendly_error(monkeypatch):
    def boom(*_args, **_kwargs):
        raise keyring.errors.NoKeyringError("no backend")

    monkeypatch.setattr(autodesk.keyring, "get_password", boom)
    store = autodesk.KeyringTokenStore(service_name="svc", username="user")
    with pytest.raises(RpcError) as excinfo:
        store.load()
    assert "keyring" in excinfo.value.message.lower()


# --- token lifecycle / injected clock ---------------------------------------


def test_ensure_access_token_returns_unexpired_token_without_http():
    store = FakeTokenStore(stored_token_dict(access_offset=3600, refresh_offset=100_000))
    router = Router()
    auth = make_auth(router=router, token_store=store)
    assert auth.ensure_access_token() == "current-access"
    assert router.requests == []


def test_ensure_access_token_refreshes_when_access_expired():
    store = FakeTokenStore(stored_token_dict(access_offset=-100, refresh_offset=100_000))
    router = Router().add(
        "POST",
        "/authentication/v2/token",
        {
            "json": {
                "access_token": "refreshed-access",
                "refresh_token": "refreshed-refresh",
                "expires_in": 3600,
                "refresh_token_expires_in": 200_000,
            }
        },
    )
    auth = make_auth(router=router, token_store=store)
    assert auth.ensure_access_token() == "refreshed-access"
    assert store.value["access_token"] == "refreshed-access"
    assert router.count("POST", "/authentication/v2/token") == 1


def test_ensure_access_token_logs_in_when_both_tokens_expired(monkeypatch):
    monkeypatch.setattr(autodesk.webbrowser, "open", lambda _url: None)
    store = FakeTokenStore()  # nothing stored at all
    router = Router().add(
        "POST",
        "/authentication/v2/token",
        {
            "json": {
                "access_token": "logged-in-access",
                "refresh_token": "logged-in-refresh",
                "expires_in": 3600,
            }
        },
    )
    auth = make_auth(router=router, token_store=store, callback_waiter=lambda *_a: "auth-code")
    assert auth.ensure_access_token() == "logged-in-access"
    assert store.value["access_token"] == "logged-in-access"


def test_token_from_payload_uses_injected_clock():
    auth = make_auth()
    token = auth._token_from_payload(
        {"access_token": "a", "refresh_token": "r", "expires_in": 3600}
    )
    assert token.access_token_expires_at_utc == iso(3600 - 30)
    # Default refresh TTL is 15 days, minus the same 30s safety margin.
    assert token.refresh_token_expires_at_utc == iso(15 * 24 * 60 * 60 - 30)


def test_login_interactive_rejects_non_local_callback():
    auth = make_auth(callback_url="https://example.com/callback")
    with pytest.raises(RpcError, match="Callback URL"):
        auth.login_interactive()


def test_login_interactive_exchanges_code_for_token(monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(autodesk.webbrowser, "open", lambda url: opened.append(url))
    store = FakeTokenStore()
    router = Router().add(
        "POST",
        "/authentication/v2/token",
        {
            "json": {
                "access_token": "fresh-access",
                "refresh_token": "fresh-refresh",
                "expires_in": 3600,
            }
        },
    )
    auth = make_auth(router=router, token_store=store, callback_waiter=lambda *_a: "the-code")
    token = auth.login_interactive()
    assert token.access_token == "fresh-access"
    assert store.value["access_token"] == "fresh-access"
    assert opened and opened[0].startswith(autodesk.AuthSessionService.authorize_endpoint)


def test_token_exchange_failure_raises_rpc_error(monkeypatch):
    monkeypatch.setattr(autodesk.webbrowser, "open", lambda _url: None)
    router = Router().add(
        "POST", "/authentication/v2/token", {"status": 400, "text": "invalid_grant"}
    )
    auth = make_auth(router=router, callback_waiter=lambda *_a: "the-code")
    with pytest.raises(RpcError, match="invalid_grant"):
        auth.login_interactive()


# --- wait_for_oauth_callback (real loopback socket) --------------------------


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _get_with_retry(url: str, params: dict, timeout: float = 5.0) -> None:
    """Fire one GET, retrying only while the server has not yet bound."""
    deadline = time.time() + timeout
    while True:
        try:
            httpx.get(url, params=params)
            return
        except httpx.ConnectError:
            if time.time() > deadline:
                raise
            time.sleep(0.02)


def drive_callback(expected_state: str, query: dict, path: str = "/cb") -> dict:
    """Run ``wait_for_oauth_callback`` in a thread and fire one redirect at it."""
    port = _free_port()
    outcome: dict = {}

    def server() -> None:
        try:
            outcome["code"] = autodesk.wait_for_oauth_callback(
                "127.0.0.1", port, path, expected_state
            )
        except BaseException as exc:  # noqa: BLE001 - re-raised to the test
            outcome["error"] = exc

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    _get_with_retry(f"http://127.0.0.1:{port}{path}", query)
    thread.join(timeout=5)
    return outcome


def test_wait_for_oauth_callback_returns_authorization_code():
    outcome = drive_callback("state-123", {"state": "state-123", "code": "the-code"})
    assert outcome.get("code") == "the-code"


def test_wait_for_oauth_callback_rejects_state_mismatch():
    outcome = drive_callback("expected-state", {"state": "tampered", "code": "c"})
    assert isinstance(outcome.get("error"), RpcError)
    assert "state mismatch" in outcome["error"].message.lower()


def test_wait_for_oauth_callback_reports_oauth_error():
    outcome = drive_callback("state-123", {"state": "state-123", "error": "access_denied"})
    assert isinstance(outcome.get("error"), RpcError)
    assert "access_denied" in outcome["error"].message


def test_wait_for_oauth_callback_requires_a_code():
    outcome = drive_callback("state-123", {"state": "state-123"})
    assert isinstance(outcome.get("error"), RpcError)
    assert "authorization code" in outcome["error"].message.lower()


# --- ApsClient browsing ------------------------------------------------------


def _hub(hub_id: str, name: str) -> dict:
    return {
        "id": hub_id,
        "attributes": {"name": name, "extension": {"type": "hubs:autodesk.core:Hub"}},
    }


def _project(project_id: str, name: str) -> dict:
    return {
        "id": project_id,
        "attributes": {
            "name": name,
            "extension": {"type": "projects:autodesk.bim360:Project"},
        },
        "relationships": {"rootFolder": {"data": {"id": f"root-{project_id}"}}},
    }


def test_list_hubs_sorts_case_insensitively():
    router = Router().add(
        "GET",
        "/project/v1/hubs",
        {"json": {"data": [_hub("h2", "Beta"), _hub("h1", "alpha")]}},
    )
    hubs = make_client(router).list_hubs()
    assert [h["name"] for h in hubs] == ["alpha", "Beta"]
    assert hubs[0]["id"] == "h1"


def test_list_projects_follows_pagination():
    router = Router()
    router.add(
        "GET",
        "page=2",
        {"json": {"data": [_project("p2", "Zeta")], "links": {}}},
    )
    router.add(
        "GET",
        "/hubs/h/projects",
        {
            "json": {
                "data": [_project("p1", "Alpha")],
                "links": {
                    "next": {
                        "href": "https://developer.api.autodesk.com/project/v1/hubs/h/projects?page=2"
                    }
                },
            }
        },
    )
    projects = make_client(router).list_projects("h")
    assert [p["id"] for p in projects] == ["p1", "p2"]
    assert projects[0]["root_folder_id"] == "root-p1"


def test_get_item_returns_tip_details():
    router = Router().add(
        "GET",
        "/items/",
        {
            "json": {
                "data": {
                    "id": "item-1",
                    "attributes": {"displayName": "Model.ifcfed", "hidden": False},
                    "relationships": {
                        "parent": {"data": {"id": "folder-1"}},
                        "tip": {"data": {"id": "v3"}},
                    },
                },
                "included": [
                    {
                        "type": "versions",
                        "id": "v3",
                        "attributes": {
                            "versionNumber": 3,
                            "lastModifiedTime": "2026-01-01T00:00:00Z",
                            "lastModifiedUserName": "Dion",
                        },
                        "relationships": {
                            "storage": {
                                "data": {"id": "urn:adsk.objects:os.object:b/o"}
                            }
                        },
                    }
                ],
            }
        },
    )
    item = make_client(router).get_item("proj-1", "item-1")
    assert item["hidden"] is False
    assert item["version_id"] == "v3"
    assert item["storage_id"] == "urn:adsk.objects:os.object:b/o"
    assert item["version_number"] == 3
    assert item["parent_folder_id"] == "folder-1"
    assert item["last_modified_user_name"] == "Dion"


def test_get_item_without_tip_is_treated_as_hidden():
    router = Router().add(
        "GET",
        "/items/",
        {"json": {"data": {"id": "item-1", "attributes": {}, "relationships": {}}}},
    )
    item = make_client(router).get_item("proj-1", "item-1")
    assert item["hidden"] is True
    assert item["storage_id"] is None
    assert item["version_id"] is None


def test_list_folder_contents_applies_extension_filter():
    router = Router().add(
        "GET",
        "/contents",
        {
            "json": {
                "data": [
                    {
                        "id": "f1",
                        "type": "folders",
                        "attributes": {"name": "Sub", "extension": {"type": "t"}},
                    },
                    {
                        "id": "i1",
                        "type": "items",
                        "attributes": {"displayName": "keep.ifcfed", "extension": {}},
                    },
                    {
                        "id": "i2",
                        "type": "items",
                        "attributes": {"displayName": "skip.txt", "extension": {}},
                    },
                ],
                "links": {},
            }
        },
    )
    entries = make_client(router).list_folder_contents(
        "proj",
        "folder",
        extension_filter=lambda e: (e["display_name"] or "").endswith(".ifcfed"),
    )
    ids = {e["id"] for e in entries}
    assert ids == {"f1", "i1"}  # folders kept, non-.ifcfed item dropped


def test_get_json_maps_http_error_to_rpc_error():
    router = Router().add(
        "GET", "/project/v1/hubs", {"status": 403, "text": "Forbidden: bad token"}
    )
    with pytest.raises(RpcError, match="Forbidden"):
        make_client(router).list_hubs()


# --- download / upload -------------------------------------------------------


def test_download_storage_to_file_writes_content_and_reports_progress(tmp_path):
    router = Router()
    router.add(
        "GET",
        "/signeds3download",
        {"json": {"url": "https://signed.example/blob"}},
    )
    router.add("GET", "signed.example/blob", {"content": b"hello world"})
    dest = tmp_path / "out.bin"
    seen: list = []
    make_client(router).download_storage_to_file(
        "urn:adsk.objects:os.object:bucket/object",
        dest,
        progress=lambda name, pct, done, total: seen.append((name, pct, done, total)),
    )
    assert dest.read_bytes() == b"hello world"
    assert seen[-1][1] == 100  # final progress callback reports 100%


def test_signed_download_url_missing_raises():
    router = Router().add("GET", "/signeds3download", {"json": {}})
    with pytest.raises(RpcError, match="URL"):
        make_client(router).download_storage_to_file(
            "urn:adsk.objects:os.object:bucket/object", "/tmp/ignored"
        )


def _upload_router() -> Router:
    router = Router()
    router.add(
        "POST", "/storage", {"json": {"data": {"id": "urn:adsk.objects:os.object:bk/obj"}}}
    )
    router.add(
        "GET",
        "/signeds3upload",
        {"json": {"uploadKey": "ukey", "urls": ["https://up.example/part1"]}},
    )
    router.add("PUT", "up.example/part1", {"status": 200})
    router.add("POST", "/signeds3upload", {"status": 200, "json": {}})
    return router


def test_upload_file_creates_new_item_when_folder_is_empty(tmp_path):
    local = tmp_path / "model.ifc"
    local.write_bytes(b"x" * 1024)
    router = _upload_router()
    router.add("GET", "/contents", {"json": {"data": [], "links": {}}})
    router.add(
        "POST",
        "/items",
        {
            "json": {
                "data": {"id": "new-item"},
                "included": [
                    {
                        "type": "versions",
                        "id": "v1",
                        "attributes": {
                            "versionNumber": 1,
                            "lastModifiedTime": "2026-01-01T00:00:00Z",
                            "lastModifiedUserName": "Dion",
                        },
                    }
                ],
            }
        },
    )
    result = make_client(router).upload_file_to_folder(
        "proj", "folder", local, display_name="model.ifc"
    )
    assert result["item_id"] == "new-item"
    assert result["version_id"] == "v1"
    assert result["version_number"] == 1
    assert router.count("PUT", "up.example/part1") == 1


def test_upload_file_creates_a_version_when_item_exists(tmp_path):
    local = tmp_path / "model.ifc"
    local.write_bytes(b"x" * 1024)
    router = _upload_router()
    router.add(
        "GET",
        "/contents",
        {
            "json": {
                "data": [
                    {
                        "id": "existing-item",
                        "type": "items",
                        "attributes": {"displayName": "model.ifc", "extension": {}},
                    }
                ],
                "links": {},
            }
        },
    )
    router.add(
        "POST",
        "/versions",
        {"json": {"data": {"id": "v7", "attributes": {"versionNumber": 7}}}},
    )
    result = make_client(router).upload_file_to_folder(
        "proj", "folder", local, display_name="model.ifc"
    )
    assert result["item_id"] == "existing-item"
    assert result["version_id"] == "v7"
    assert result["version_number"] == 7


def test_upload_rejects_missing_local_file(tmp_path):
    with pytest.raises(RpcError, match="does not exist"):
        make_client(Router()).upload_file_to_folder(
            "proj", "folder", tmp_path / "missing.ifc"
        )
