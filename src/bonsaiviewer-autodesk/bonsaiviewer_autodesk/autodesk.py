from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import math
import secrets
import urllib.parse
import webbrowser
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable

import httpx
import keyring
import keyring.errors

from bonsaiviewer_autodesk.rpc import JSONRPC_INTERNAL_ERROR, RpcError


Progress = Callable[[str, str, "int | None"], None]

# (host, port, path, expected_state) -> authorization code
CallbackWaiter = Callable[[str, int, str, str], str]


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _no_keyring_error() -> RpcError:
    return RpcError(
        JSONRPC_INTERNAL_ERROR,
        "No secure keyring backend is available. On macOS, use Keychain; "
        "on Windows, use Credential Manager; on Linux, install a Secret Service "
        "backend such as gnome-keyring or KWallet.",
    )


class KeyringTokenStore:
    def __init__(self, *, service_name: str, username: str) -> None:
        self.service_name = service_name
        self.username = username

    def load(self) -> dict[str, Any] | None:
        try:
            raw = keyring.get_password(self.service_name, self.username)
        except keyring.errors.NoKeyringError as exc:
            raise _no_keyring_error() from exc
        return json.loads(raw) if raw else None

    def save(self, value: dict[str, Any]) -> None:
        try:
            keyring.set_password(self.service_name, self.username, json.dumps(value))
        except keyring.errors.NoKeyringError as exc:
            raise _no_keyring_error() from exc

    def delete(self) -> None:
        try:
            keyring.delete_password(self.service_name, self.username)
        except keyring.errors.PasswordDeleteError:
            pass
        except keyring.errors.NoKeyringError as exc:
            raise _no_keyring_error() from exc


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def generate_code_verifier() -> str:
    return _base64url(secrets.token_bytes(48))


def generate_code_challenge(verifier: str) -> str:
    return _base64url(hashlib.sha256(verifier.encode("ascii")).digest())


@dataclass
class StoredToken:
    client_id: str
    access_token: str
    refresh_token: str
    access_token_expires_at_utc: str
    refresh_token_expires_at_utc: str
    scope: str

    @property
    def access_token_expires_at(self) -> dt.datetime:
        return dt.datetime.fromisoformat(self.access_token_expires_at_utc)

    @property
    def refresh_token_expires_at(self) -> dt.datetime:
        return dt.datetime.fromisoformat(self.refresh_token_expires_at_utc)


def _noop_progress(_phase: str, _message: str, _percent: int | None = None) -> None:
    return


def wait_for_oauth_callback(host: str, port: int, path: str, expected_state: str) -> str:
    """Block on a single OAuth redirect to ``http://host:port/path`` and return
    the authorization code. Raises ``RpcError`` on an OAuth error, a ``state``
    mismatch, or a missing code. This is the default ``callback_waiter`` for
    :class:`AuthSessionService`; tests inject a stub instead."""
    result: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != path:
                self.send_response(404)
                self.end_headers()
                return
            query = urllib.parse.parse_qs(parsed.query)
            result["state"] = query.get("state", [""])[0]
            result["code"] = query.get("code", [""])[0]
            result["error"] = query.get("error", [""])[0]
            body = b"<html><body><h2>Authentication complete. You can close this window.</h2></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer((host, port), Handler)
    server.handle_request()
    server.server_close()

    if result.get("error"):
        raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk returned OAuth error '{result['error']}'.")
    if result.get("state") != expected_state:
        raise RpcError(JSONRPC_INTERNAL_ERROR, "OAuth state mismatch.")
    code = result.get("code", "")
    if not code:
        raise RpcError(JSONRPC_INTERNAL_ERROR, "OAuth callback did not return an authorization code.")
    return code


class AuthSessionService:
    authorize_endpoint = "https://developer.api.autodesk.com/authentication/v2/authorize"
    token_endpoint = "https://developer.api.autodesk.com/authentication/v2/token"

    def __init__(
        self,
        *,
        client_id: str,
        callback_url: str,
        scope: str,
        token_store: KeyringTokenStore,
        transport: httpx.BaseTransport | None = None,
        now: Callable[[], dt.datetime] | None = None,
        callback_waiter: CallbackWaiter | None = None,
    ) -> None:
        self.client_id = client_id
        self.callback_url = callback_url
        self.scope = scope
        self.token_store = token_store
        self.http = httpx.Client(timeout=60, transport=transport)
        self._now = now or _utcnow
        self._callback_waiter = callback_waiter or wait_for_oauth_callback

    def get_token(self) -> StoredToken | None:
        raw = self.token_store.load()
        return StoredToken(**raw) if raw else None

    def ensure_access_token(self, progress: Progress = _noop_progress) -> str:
        token = self.get_token()
        now = self._now()
        if token and token.access_token_expires_at > now + dt.timedelta(minutes=1):
            return token.access_token
        if token and token.refresh_token_expires_at > now + dt.timedelta(minutes=1):
            return self._refresh(token, progress).access_token
        return self.login_interactive(progress).access_token

    def login_interactive(self, progress: Progress = _noop_progress) -> StoredToken:
        progress("auth", "Preparing Autodesk sign-in", None)
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        state = secrets.token_hex(16)
        callback = urllib.parse.urlparse(self.callback_url)
        if callback.scheme != "http" or callback.hostname not in {"127.0.0.1", "localhost"}:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "Callback URL must be http://localhost or http://127.0.0.1.")

        query = urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.callback_url,
                "scope": self.scope,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": state,
            }
        )
        authorize_url = f"{self.authorize_endpoint}?{query}"

        progress("auth", "Opening browser for Autodesk sign-in", None)
        webbrowser.open(authorize_url)
        code = self._callback_waiter(
            callback.hostname or "127.0.0.1",
            callback.port or 80,
            callback.path or "/",
            state,
        )

        progress("auth", "Exchanging authorization code for token", None)
        response = self.http.post(
            self.token_endpoint,
            data={
                "client_id": self.client_id,
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": self.callback_url,
            },
        )
        if response.is_error:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Token exchange failed: {response.text}")
        token = self._token_from_payload(response.json())
        self.token_store.save(asdict(token))
        progress("auth", "Signed in to Autodesk", 100)
        return token

    def _refresh(self, token: StoredToken, progress: Progress) -> StoredToken:
        progress("auth", "Refreshing Autodesk session", None)
        response = self.http.post(
            self.token_endpoint,
            data={
                "client_id": self.client_id,
                "grant_type": "refresh_token",
                "refresh_token": token.refresh_token,
                "scope": self.scope,
            },
        )
        if response.is_error:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Token refresh failed: {response.text}")
        refreshed = self._token_from_payload(response.json())
        self.token_store.save(asdict(refreshed))
        progress("auth", "Session refreshed", 100)
        return refreshed

    def _token_from_payload(self, payload: dict[str, Any]) -> StoredToken:
        now = self._now()
        refresh_ttl = int(payload.get("refresh_token_expires_in", 15 * 24 * 60 * 60))
        return StoredToken(
            client_id=self.client_id,
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"],
            access_token_expires_at_utc=(now + dt.timedelta(seconds=int(payload["expires_in"]) - 30)).isoformat(),
            refresh_token_expires_at_utc=(now + dt.timedelta(seconds=refresh_ttl - 30)).isoformat(),
            scope=self.scope,
        )

class ApsClient:
    def __init__(self, auth: AuthSessionService, *, transport: httpx.BaseTransport | None = None) -> None:
        self.auth = auth
        self.http = httpx.Client(timeout=120, transport=transport)

    # Browsing -----------------------------------------------------------------

    def list_hubs(self) -> list[dict[str, Any]]:
        payload = self._get_json("https://developer.api.autodesk.com/project/v1/hubs")
        hubs = [
            {
                "id": item["id"],
                "name": item["attributes"]["name"],
                "extension_type": item["attributes"]["extension"]["type"],
            }
            for item in payload.get("data", [])
        ]
        hubs.sort(key=lambda h: (h["name"] or "").casefold())
        return hubs

    def list_projects(self, hub_id: str) -> list[dict[str, Any]]:
        url = f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects"
        projects: list[dict[str, Any]] = []
        while url:
            payload = self._get_json(url)
            for item in payload.get("data", []):
                projects.append(
                    {
                        "id": item["id"],
                        "name": item["attributes"]["name"],
                        "extension_type": item["attributes"]["extension"]["type"],
                        "root_folder_id": item["relationships"]["rootFolder"]["data"]["id"],
                    }
                )
            url = payload.get("links", {}).get("next", {}).get("href", "") or ""
        projects.sort(key=lambda p: (p["name"] or "").casefold())
        return projects

    def list_top_folders(self, hub_id: str, project_id: str) -> list[dict[str, Any]]:
        payload = self._get_json(
            f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects/{project_id}/topFolders"
        )
        folders = [self._entry(item) for item in payload.get("data", [])]
        folders.sort(key=lambda e: (e.get("display_name") or "").casefold())
        return folders

    def list_folder_contents(
        self,
        project_id: str,
        folder_id: str,
        *,
        object_types: list[str] | None = None,
        extension_filter: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[dict[str, Any]]:
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}/contents"
        if object_types:
            query = [("filter[type]", value) for value in object_types]
            url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        entries: list[dict[str, Any]] = []
        while url:
            payload = self._get_json(url)
            for item in payload.get("data", []):
                entry = self._entry(item)
                if extension_filter and entry["type"] == "items" and not extension_filter(entry):
                    continue
                entries.append(entry)
            url = payload.get("links", {}).get("next", {}).get("href", "") or ""
        entries.sort(key=lambda e: (e.get("display_name") or "").casefold())
        return entries

    def get_item(self, project_id: str, item_id: str) -> dict[str, Any]:
        """Return the item plus its current tip in a single request.

        ``hidden`` reflects the item's soft-delete state (BIM 360 / ACC mark
        deleted items as ``hidden: true``; the storage URL may still resolve
        to a stale copy, so callers must check this before downloading).
        """
        payload = self._get_json(
            f"https://developer.api.autodesk.com/data/v1/projects/{urllib.parse.quote(project_id, safe='')}"
            f"/items/{urllib.parse.quote(item_id, safe='')}?include=tip"
        )
        item = payload["data"]
        item_attributes = item.get("attributes", {})
        parent_folder_id = self._relationship_id(item, "parent")
        tip_id = self._relationship_id(item, "tip")
        tip: dict[str, Any] | None = None
        for included in payload.get("included", []):
            if included.get("type") == "versions" and included.get("id") == tip_id:
                tip = included
                break

        if tip is None:
            return {
                "id": item["id"],
                "display_name": item_attributes.get("displayName")
                or item_attributes.get("name")
                or item["id"],
                "hidden": True,
                "version_id": None,
                "storage_id": None,
                "version_number": None,
                "last_modified_time_utc": None,
                "last_modified_user_name": None,
                "parent_folder_id": parent_folder_id,
            }

        tip_attributes = tip.get("attributes", {})
        return {
            "id": item["id"],
            "display_name": tip_attributes.get("displayName")
            or tip_attributes.get("name")
            or item_attributes.get("displayName")
            or item["id"],
            "hidden": bool(item_attributes.get("hidden", False)),
            "version_id": tip["id"],
            "storage_id": self._relationship_id(tip, "storage"),
            "version_number": tip_attributes.get("versionNumber"),
            "last_modified_time_utc": tip_attributes.get("lastModifiedTime"),
            "last_modified_user_name": tip_attributes.get("lastModifiedUserName"),
            "parent_folder_id": parent_folder_id,
        }

    # Download / upload --------------------------------------------------------

    def download_storage_to_file(
        self,
        storage_id: str,
        destination_path: Path,
        *,
        progress: Callable[[str, int | None, int | None, int | None], None] | None = None,
    ) -> None:
        bucket_key, object_key = self._parse_storage_id(storage_id)
        signed_url = self._get_signed_download_url(bucket_key, object_key)
        self._download_to_file(signed_url, destination_path, progress)

    def upload_file_to_folder(
        self,
        project_id: str,
        folder_id: str,
        local_path: Path,
        *,
        display_name: str | None = None,
        progress: Callable[[str, int | None, int | None, int | None], None] | None = None,
    ) -> dict[str, Any]:
        if not local_path.exists():
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Local file '{local_path}' does not exist.")
        file_name = display_name or local_path.name
        storage_id = self._create_storage(project_id, folder_id, file_name)
        bucket_key, object_key = self._parse_storage_id(storage_id)
        self._upload_local_file_to_oss(bucket_key, object_key, local_path, progress)
        existing_item = self._find_item_in_folder(project_id, folder_id, file_name)
        if existing_item is not None:
            return self._create_version(project_id, existing_item["id"], file_name, storage_id)
        return self._create_item(project_id, folder_id, file_name, storage_id)

    # HTTP helpers -------------------------------------------------------------

    def _get_json(self, url: str) -> dict[str, Any]:
        token = self.auth.ensure_access_token()
        try:
            response = self.http.get(url, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        token = self.auth.ensure_access_token()
        try:
            response = self.http.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/vnd.api+json",
                    "Accept": "application/vnd.api+json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _get_signed_download_url(self, bucket_key: str, object_key: str) -> str:
        payload = self._get_json(
            "https://developer.api.autodesk.com/oss/v2/buckets/"
            f"{urllib.parse.quote(bucket_key, safe='')}/objects/"
            f"{urllib.parse.quote(object_key, safe='')}/signeds3download"
        )
        url = payload.get("url")
        if not isinstance(url, str) or not url:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "Signed download URL response did not contain a URL.")
        return url

    def _download_to_file(
        self,
        url: str,
        destination_path: Path,
        progress: Callable[[str, int | None, int | None, int | None], None] | None,
    ) -> None:
        try:
            with self.http.stream("GET", url) as response:
                response.raise_for_status()
                total_bytes: int | None = None
                header_value = response.headers.get("Content-Length")
                if header_value and header_value.isdigit():
                    total_bytes = int(header_value)
                downloaded_bytes = 0
                with open(destination_path, "wb") as handle:
                    for chunk in response.iter_bytes():
                        handle.write(chunk)
                        downloaded_bytes += len(chunk)
                        if progress and total_bytes:
                            percent = min(100, int((downloaded_bytes / total_bytes) * 100))
                            progress(destination_path.name, percent, downloaded_bytes, total_bytes)
                        elif progress:
                            progress(destination_path.name, None, downloaded_bytes, total_bytes)
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _create_storage(self, project_id: str, folder_id: str, file_name: str) -> str:
        payload = self._post_json(
            f"https://developer.api.autodesk.com/data/v1/projects/{urllib.parse.quote(project_id, safe='')}/storage",
            {
                "jsonapi": {"version": "1.0"},
                "data": {
                    "type": "objects",
                    "attributes": {"name": file_name},
                    "relationships": {"target": {"data": {"type": "folders", "id": folder_id}}},
                },
            },
        )
        storage_id = payload.get("data", {}).get("id")
        if not isinstance(storage_id, str) or not storage_id:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "Storage creation did not return an object id.")
        return storage_id

    def _upload_local_file_to_oss(
        self,
        bucket_key: str,
        object_key: str,
        local_path: Path,
        progress: Callable[[str, int | None, int | None, int | None], None] | None,
    ) -> None:
        file_size = local_path.stat().st_size
        chunk_size = 5 * 1024 * 1024
        total_parts = max(1, math.ceil(file_size / chunk_size))
        upload_key: str | None = None
        parts_uploaded = 0
        bytes_uploaded = 0

        with open(local_path, "rb") as handle:
            while parts_uploaded < total_parts:
                parts_to_request = min(total_parts - parts_uploaded, 5)
                first_part = parts_uploaded + 1
                signed = self._get_signed_upload_urls(
                    bucket_key,
                    object_key,
                    upload_key=upload_key,
                    first_part=first_part,
                    parts=parts_to_request,
                )
                if upload_key is None:
                    upload_key = signed.get("uploadKey")
                urls = signed.get("urls", [])
                if not isinstance(urls, list) or not urls:
                    raise RpcError(JSONRPC_INTERNAL_ERROR, "Upload URL response did not contain upload URLs.")
                for url in urls:
                    if parts_uploaded >= total_parts:
                        break
                    chunk = handle.read(chunk_size)
                    if not chunk:
                        break
                    self._put_bytes(str(url), chunk)
                    parts_uploaded += 1
                    bytes_uploaded += len(chunk)
                    if progress:
                        percent = 100 if file_size == 0 else min(100, int((bytes_uploaded / file_size) * 100))
                        progress(local_path.name, percent, bytes_uploaded, file_size)

        if not upload_key:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "Upload did not return an upload key.")
        self._complete_signed_upload(bucket_key, object_key, upload_key)

    def _get_signed_upload_urls(
        self,
        bucket_key: str,
        object_key: str,
        *,
        upload_key: str | None,
        first_part: int,
        parts: int,
    ) -> dict[str, Any]:
        token = self.auth.ensure_access_token()
        params: dict[str, Any] = {"minutesExpiration": 10, "firstPart": first_part, "parts": parts}
        if upload_key:
            params["uploadKey"] = upload_key
        try:
            response = self.http.get(
                "https://developer.api.autodesk.com/oss/v2/buckets/"
                f"{urllib.parse.quote(bucket_key, safe='')}/objects/"
                f"{urllib.parse.quote(object_key, safe='')}/signeds3upload",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _complete_signed_upload(self, bucket_key: str, object_key: str, upload_key: str) -> None:
        token = self.auth.ensure_access_token()
        try:
            response = self.http.post(
                "https://developer.api.autodesk.com/oss/v2/buckets/"
                f"{urllib.parse.quote(bucket_key, safe='')}/objects/"
                f"{urllib.parse.quote(object_key, safe='')}/signeds3upload",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"uploadKey": upload_key},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _put_bytes(self, url: str, content: bytes) -> None:
        try:
            response = self.http.put(url, content=content, headers={"Content-Type": "application/octet-stream"})
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text.strip()
            raise RpcError(JSONRPC_INTERNAL_ERROR, body or f"HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RpcError(JSONRPC_INTERNAL_ERROR, str(exc)) from exc

    def _find_item_in_folder(self, project_id: str, folder_id: str, file_name: str) -> dict[str, Any] | None:
        children = self.list_folder_contents(project_id, folder_id, object_types=["items"])
        return next(
            (
                child for child in children
                if self._entry_name_matches(child, file_name)
            ),
            None,
        )

    def _create_version(self, project_id: str, item_id: str, file_name: str, storage_id: str) -> dict[str, Any]:
        payload = self._post_json(
            f"https://developer.api.autodesk.com/data/v1/projects/{urllib.parse.quote(project_id, safe='')}/versions",
            {
                "jsonapi": {"version": "1.0"},
                "data": {
                    "type": "versions",
                    "attributes": {
                        "name": file_name,
                        "extension": {"type": "versions:autodesk.bim360:File", "version": "1.0"},
                    },
                    "relationships": {
                        "item": {"data": {"type": "items", "id": item_id}},
                        "storage": {"data": {"type": "objects", "id": storage_id}},
                    },
                },
            },
        )
        version = payload["data"]
        attributes = version.get("attributes", {})
        return {
            "item_id": item_id,
            "version_id": version["id"],
            "display_name": file_name,
            "version_number": attributes.get("versionNumber"),
            "last_modified_time_utc": attributes.get("lastModifiedTime"),
            "last_modified_user_name": attributes.get("lastModifiedUserName"),
        }

    def _create_item(self, project_id: str, folder_id: str, file_name: str, storage_id: str) -> dict[str, Any]:
        payload = self._post_json(
            f"https://developer.api.autodesk.com/data/v1/projects/{urllib.parse.quote(project_id, safe='')}/items",
            {
                "jsonapi": {"version": "1.0"},
                "data": {
                    "type": "items",
                    "attributes": {
                        "displayName": file_name,
                        "extension": {"type": "items:autodesk.bim360:File", "version": "1.0"},
                    },
                    "relationships": {
                        "tip": {"data": {"type": "versions", "id": "1"}},
                        "parent": {"data": {"type": "folders", "id": folder_id}},
                    },
                },
                "included": [
                    {
                        "type": "versions",
                        "id": "1",
                        "attributes": {
                            "name": file_name,
                            "extension": {"type": "versions:autodesk.bim360:File", "version": "1.0"},
                        },
                        "relationships": {"storage": {"data": {"type": "objects", "id": storage_id}}},
                    }
                ],
            },
        )
        item = payload["data"]
        version_id = "1"
        version_number: Any = 1
        last_modified_time: Any = None
        last_modified_user: Any = None
        for included in payload.get("included", []):
            if included.get("type") == "versions":
                version_id = included.get("id") or version_id
                attributes = included.get("attributes", {})
                version_number = attributes.get("versionNumber", version_number)
                last_modified_time = attributes.get("lastModifiedTime")
                last_modified_user = attributes.get("lastModifiedUserName")
                break
        return {
            "item_id": item["id"],
            "version_id": version_id,
            "display_name": file_name,
            "version_number": version_number,
            "last_modified_time_utc": last_modified_time,
            "last_modified_user_name": last_modified_user,
        }

    # Static helpers -----------------------------------------------------------

    @staticmethod
    def _parse_storage_id(storage_id: str) -> tuple[str, str]:
        marker = "urn:adsk.objects:os.object:"
        if not storage_id.startswith(marker):
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Unsupported storage identifier '{storage_id}'.")
        path = storage_id[len(marker):]
        slash = path.find("/")
        if slash <= 0 or slash == len(path) - 1:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Malformed storage identifier '{storage_id}'.")
        return path[:slash], path[slash + 1 :]

    @staticmethod
    def _entry(item: dict[str, Any]) -> dict[str, Any]:
        attributes = item["attributes"]
        return {
            "id": item["id"],
            "type": item["type"],
            "display_name": attributes.get("displayName") or attributes.get("name") or "",
            "name": attributes.get("name"),
            "extension_type": attributes.get("extension", {}).get("type", ""),
        }

    @staticmethod
    def _relationship_id(data: dict[str, Any], name: str) -> str | None:
        rel_data = data.get("relationships", {}).get(name, {}).get("data")
        if isinstance(rel_data, dict):
            rel_id = rel_data.get("id")
            return rel_id if isinstance(rel_id, str) and rel_id else None
        if isinstance(rel_data, list) and rel_data:
            rel_id = rel_data[0].get("id")
            return rel_id if isinstance(rel_id, str) and rel_id else None
        return None

    @staticmethod
    def _entry_name_matches(entry: dict[str, Any], expected_name: str) -> bool:
        display_name = str(entry.get("display_name") or "").lower()
        raw_name = str(entry.get("name") or "").lower()
        expected = expected_name.lower()
        return display_name == expected or raw_name == expected
