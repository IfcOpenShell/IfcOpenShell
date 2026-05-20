from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from bonsaiviewer_autodesk import cache, settings
from bonsaiviewer_autodesk.autodesk import ApsClient, AuthSessionService, KeyringTokenStore
from bonsaiviewer_autodesk.rpc import JSONRPC_INTERNAL_ERROR, JSONRPC_INVALID_PARAMS, RpcError
from bonsaiviewer_autodesk.ui import BrowseDialog, SettingsDialog, progress_dialog, prompt_for_filename


ApsProgress = Callable[[str, "int | None"], None]
Report = Callable[[str, str, "int | None"], None]


def _download_callback(report: Report, index: int = 0, total: int = 0) -> ApsProgress:
    """Adapt ProgressDialog.report (3-arg) to the APS download callback (2-arg).

    index/total render "(i/N)" suffix when batching; pass 0 (the default) for
    single-file downloads to omit the suffix.
    """
    def cb(name: str, percent: int | None) -> None:
        suffix = f" ({index}/{total})" if total else ""
        report("download", f"Downloading {name}{suffix}", percent)
    return cb


def _upload_callback(report: Report) -> ApsProgress:
    def cb(name: str, percent: int | None) -> None:
        report("upload", f"Uploading {name}", percent)
    return cb


CONNECTOR_ID = "autodesk"
KEYRING_SERVICE = "bonsaiviewer-autodesk"
DEFAULT_SCOPE = "data:read data:write data:create"


class AutodeskConnector:
    def __init__(self) -> None:
        self.auth: AuthSessionService | None = None
        self.aps: ApsClient | None = None
        self.reload_credentials()

    def reload_credentials(self) -> None:
        """Rebuild auth + APS from current settings. Safe to call any time."""
        client_id = settings.load_client_id()
        if not client_id:
            self.auth = None
            self.aps = None
            return
        token_store = KeyringTokenStore(service_name=KEYRING_SERVICE, username=client_id)
        callback_url = f"http://localhost:{settings.stored_callback_port()}/"
        self.auth = AuthSessionService(
            client_id=client_id,
            callback_url=callback_url,
            scope=DEFAULT_SCOPE,
            token_store=token_store,
        )
        self.aps = ApsClient(self.auth)

    def _require_aps(self) -> tuple[AuthSessionService, ApsClient]:
        if self.auth is None or self.aps is None:
            raise RpcError(
                JSONRPC_INTERNAL_ERROR,
                "Autodesk client id is not configured. Open the connector settings to set it.",
            )
        return self.auth, self.aps

    def handlers(self) -> dict[str, Any]:
        return {
            "pull_ifcfed_interactive": self.pull_ifcfed_interactive,
            "pull_ifcfed": self.pull_ifcfed,
            "pull_models": self.pull_models,
            "pull_models_interactive": self.pull_models_interactive,
            "push_ifcfed_interactive": self.push_ifcfed_interactive,
            "push_ifcfed": self.push_ifcfed,
            "push_model_interactive": self.push_model_interactive,
            "push_model": self.push_model,
            "open_settings": self.open_settings,
        }

    # ---- open_settings ------------------------------------------------------

    def open_settings(self, _params: Any) -> dict[str, Any]:
        SettingsDialog(connector=self).run()
        return {}

    # ---- pull_ifcfed_interactive --------------------------------------------

    def pull_ifcfed_interactive(self, _params: Any) -> dict[str, Any]:
        auth, aps = self._require_aps()
        chosen = BrowseDialog(auth=auth, aps=aps, mode="ifcfed").run()
        hub = chosen["hub"]
        project = chosen["project"]
        entry = chosen["entry"]
        with progress_dialog("Downloading project") as report:
            path = self._download_ifcfed(
                aps=aps,
                hub_id=hub["id"],
                project_id=project["id"],
                item_id=entry["id"],
                display_name=entry["display_name"],
                progress=_download_callback(report),
            )
        return {"path": str(path)}

    # ---- pull_ifcfed --------------------------------------------------------

    def pull_ifcfed(self, params: Any) -> dict[str, Any]:
        _, aps = self._require_aps()
        manifest = _require_object(params, "params")
        hub_id = _require_string(manifest, "hub_id")
        project_id = _require_string(manifest, "project_id")
        item_id = _require_string(manifest, "item_id")
        display_name = manifest.get("display_name") or item_id
        with progress_dialog("Downloading project") as report:
            path = self._download_ifcfed(
                aps=aps,
                hub_id=hub_id,
                project_id=project_id,
                item_id=item_id,
                display_name=display_name,
                progress=_download_callback(report),
            )
        return {"path": str(path)}

    def _download_ifcfed(
        self,
        *,
        aps: ApsClient,
        hub_id: str,
        project_id: str,
        item_id: str,
        display_name: str,
        progress: ApsProgress | None = None,
    ) -> Path:
        item = aps.get_item(project_id, item_id)
        if item["hidden"]:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{item_id}' has been deleted.")
        storage_id = item["storage_id"]
        if not isinstance(storage_id, str):
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{item_id}' has no downloadable storage.")
        file_name = item["display_name"] or display_name or item_id
        if not file_name.lower().endswith(".ifcfed"):
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Item '{file_name}' is not an .ifcfed file.")

        directory = cache.prepare_sole_child_dir(cache.ifcfed_dir(project_id, item_id))
        ifcfed_path = directory / file_name
        aps.download_storage_to_file(storage_id, ifcfed_path, progress=progress)
        cache.write_manifest(
            ifcfed_path,
            {
                "connector": CONNECTOR_ID,
                "hub_id": hub_id,
                "project_id": project_id,
                "item_id": item_id,
                "display_name": file_name,
            },
        )
        return ifcfed_path

    # ---- pull_models --------------------------------------------------------

    def pull_models(self, params: Any) -> list[dict[str, Any] | None]:
        _, aps = self._require_aps()
        models = _require_array(params, "params")
        results: list[dict[str, Any] | None] = []
        total = len(models)
        with progress_dialog("Downloading models") as report:
            for index, model in enumerate(models):
                callback = _download_callback(report, index=index + 1, total=total)
                try:
                    results.append(self._resolve_model(aps, model, progress=callback))
                except RpcError as exc:
                    print(f"pull_models[{index}] skipped: {exc.message}", file=sys.stderr)
                    results.append(None)
                except Exception as exc:
                    print(f"pull_models[{index}] skipped: {exc}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    results.append(None)
        return results

    def _resolve_model(
        self,
        aps: ApsClient,
        model: Any,
        *,
        progress: ApsProgress | None = None,
    ) -> dict[str, Any] | None:
        if not isinstance(model, dict):
            raise RpcError(JSONRPC_INVALID_PARAMS, "Each model entry must be an object.")
        source = model.get("source")
        if not isinstance(source, dict):
            raise RpcError(JSONRPC_INVALID_PARAMS, "Each model entry must have a 'source' object.")
        if source.get("connector") != CONNECTOR_ID:
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Source connector is not '{CONNECTOR_ID}'.")
        project_id = _require_string(source, "project_id")
        item_id = _require_string(source, "item_id")
        display_name_hint = model.get("display_name") or item_id

        item = aps.get_item(project_id, item_id)
        if item["hidden"]:
            print(f"Autodesk item '{item_id}' is hidden/deleted; returning null.", file=sys.stderr)
            return None

        storage_id = item["storage_id"]
        if not isinstance(storage_id, str):
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{item_id}' has no downloadable storage.")
        file_name = item["display_name"] or display_name_hint
        version_id = item["version_id"]

        directory = cache.model_dir(project_id, item_id, version_id)
        model_path = directory / file_name
        if not model_path.exists():
            cache.prepare_sole_child_dir(directory)
            aps.download_storage_to_file(storage_id, model_path, progress=progress)

        return {
            "path": str(model_path),
            "metadata": _build_metadata(item),
        }

    # ---- pull_models_interactive --------------------------------------------

    def pull_models_interactive(self, _params: Any) -> list[dict[str, Any]]:
        auth, aps = self._require_aps()
        chosen = BrowseDialog(auth=auth, aps=aps, mode="model").run()
        hub = chosen["hub"]
        project = chosen["project"]
        entry = chosen["entry"]
        item = aps.get_item(project["id"], entry["id"])
        if item["hidden"]:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "The selected Autodesk item has been deleted.")
        storage_id = item["storage_id"]
        if not isinstance(storage_id, str):
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{entry['id']}' has no downloadable storage.")

        file_name = item["display_name"] or entry["display_name"] or entry["id"]
        version_id = item["version_id"]

        directory = cache.model_dir(project["id"], entry["id"], version_id)
        model_path = directory / file_name
        if not model_path.exists():
            cache.prepare_sole_child_dir(directory)
            with progress_dialog("Downloading model") as report:
                aps.download_storage_to_file(
                    storage_id, model_path, progress=_download_callback(report)
                )

        return [
            {
                "display_name": file_name,
                "source": {
                    "connector": CONNECTOR_ID,
                    "hub_id": hub["id"],
                    "project_id": project["id"],
                    "item_id": entry["id"],
                },
                "path": str(model_path),
                "metadata": _build_metadata(item),
            }
        ]

    # ---- push_ifcfed_interactive --------------------------------------------

    def push_ifcfed_interactive(self, params: Any) -> dict[str, Any]:
        auth, aps = self._require_aps()
        params_obj = _require_object(params, "params")
        local_path = Path(_require_string(params_obj, "path"))
        if not local_path.exists():
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Local file '{local_path}' does not exist.")
        if not local_path.name.lower().endswith(".ifcfed"):
            raise RpcError(JSONRPC_INVALID_PARAMS, "push_ifcfed_interactive expects an .ifcfed file.")

        chosen = BrowseDialog(auth=auth, aps=aps, mode="destination").run()
        hub = chosen["hub"]
        project = chosen["project"]
        folder = chosen["entry"]

        file_name = prompt_for_filename(
            title="Save Project",
            label="Save .ifcfed as:",
            default=local_path.name,
        )
        if not file_name:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "User cancelled save to cloud.")
        if not file_name.lower().endswith(".ifcfed"):
            file_name = file_name + ".ifcfed"

        with progress_dialog("Uploading project") as report:
            uploaded = aps.upload_file_to_folder(
                project["id"],
                folder["id"],
                local_path,
                display_name=file_name,
                progress=_upload_callback(report),
            )

        directory = cache.prepare_sole_child_dir(cache.ifcfed_dir(project["id"], uploaded["item_id"]))
        cached_path = directory / file_name
        cached_path.write_bytes(local_path.read_bytes())
        cache.write_manifest(
            cached_path,
            {
                "connector": CONNECTOR_ID,
                "hub_id": hub["id"],
                "project_id": project["id"],
                "item_id": uploaded["item_id"],
                "display_name": file_name,
            },
        )
        return {"path": str(cached_path)}

    # ---- push_ifcfed --------------------------------------------------------

    def push_ifcfed(self, params: Any) -> dict[str, Any]:
        _, aps = self._require_aps()
        params_obj = _require_object(params, "params")
        local_path = Path(_require_string(params_obj, "path"))
        if not local_path.exists():
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Local file '{local_path}' does not exist.")
        if not local_path.name.lower().endswith(".ifcfed"):
            raise RpcError(JSONRPC_INVALID_PARAMS, "push_ifcfed expects an .ifcfed file.")

        manifest = params_obj.get("manifest")
        if not isinstance(manifest, dict):
            raise RpcError(JSONRPC_INVALID_PARAMS, "'manifest' must be a JSON object.")
        if manifest.get("connector") != CONNECTOR_ID:
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Manifest connector is not '{CONNECTOR_ID}'.")
        hub_id = _require_string(manifest, "hub_id")
        project_id = _require_string(manifest, "project_id")
        item_id = _require_string(manifest, "item_id")

        item = aps.get_item(project_id, item_id)
        if item["hidden"]:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{item_id}' has been deleted.")
        folder_id = item.get("parent_folder_id")
        if not isinstance(folder_id, str) or not folder_id:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Cannot resolve parent folder for item '{item_id}'.")
        file_name = manifest.get("display_name") or item.get("display_name") or local_path.name

        with progress_dialog("Uploading project") as report:
            uploaded = aps.upload_file_to_folder(
                project_id,
                folder_id,
                local_path,
                display_name=file_name,
                progress=_upload_callback(report),
            )

        directory = cache.prepare_sole_child_dir(cache.ifcfed_dir(project_id, uploaded["item_id"]))
        cached_path = directory / file_name
        cached_path.write_bytes(local_path.read_bytes())
        cache.write_manifest(
            cached_path,
            {
                "connector": CONNECTOR_ID,
                "hub_id": hub_id,
                "project_id": project_id,
                "item_id": uploaded["item_id"],
                "display_name": file_name,
            },
        )
        return {"path": str(cached_path)}

    # ---- push_model_interactive ---------------------------------------------

    def push_model_interactive(self, params: Any) -> dict[str, Any]:
        auth, aps = self._require_aps()
        params_obj = _require_object(params, "params")
        local_path = Path(_require_string(params_obj, "path"))
        if not local_path.exists():
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Local file '{local_path}' does not exist.")

        chosen = BrowseDialog(auth=auth, aps=aps, mode="destination").run()
        hub = chosen["hub"]
        project = chosen["project"]
        folder = chosen["entry"]

        file_name = prompt_for_filename(
            title="Save Model",
            label="Save model as:",
            default=local_path.name,
        )
        if not file_name:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "User cancelled save to cloud.")

        with progress_dialog("Uploading model") as report:
            uploaded = aps.upload_file_to_folder(
                project["id"],
                folder["id"],
                local_path,
                display_name=file_name,
                progress=_upload_callback(report),
            )

        directory = cache.model_dir(project["id"], uploaded["item_id"], uploaded["version_id"])
        cache.prepare_sole_child_dir(directory)
        cached_path = directory / file_name
        cached_path.write_bytes(local_path.read_bytes())

        return {
            "display_name": file_name,
            "path": str(cached_path),
            "source": {
                "connector": CONNECTOR_ID,
                "hub_id": hub["id"],
                "project_id": project["id"],
                "item_id": uploaded["item_id"],
            },
            "metadata": _build_metadata(uploaded),
        }

    # ---- push_model ---------------------------------------------------------

    def push_model(self, params: Any) -> dict[str, Any]:
        _, aps = self._require_aps()
        params_obj = _require_object(params, "params")
        local_path = Path(_require_string(params_obj, "path"))
        if not local_path.exists():
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Local file '{local_path}' does not exist.")

        source = params_obj.get("source")
        if not isinstance(source, dict):
            raise RpcError(JSONRPC_INVALID_PARAMS, "'source' must be a JSON object.")
        if source.get("connector") != CONNECTOR_ID:
            raise RpcError(JSONRPC_INVALID_PARAMS, f"Source connector is not '{CONNECTOR_ID}'.")
        hub_id = _require_string(source, "hub_id")
        project_id = _require_string(source, "project_id")
        item_id = _require_string(source, "item_id")

        item = aps.get_item(project_id, item_id)
        if item["hidden"]:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Autodesk item '{item_id}' has been deleted.")
        folder_id = item.get("parent_folder_id")
        if not isinstance(folder_id, str) or not folder_id:
            raise RpcError(JSONRPC_INTERNAL_ERROR, f"Cannot resolve parent folder for item '{item_id}'.")
        file_name = item.get("display_name") or local_path.name

        with progress_dialog("Uploading model") as report:
            uploaded = aps.upload_file_to_folder(
                project_id,
                folder_id,
                local_path,
                display_name=file_name,
                progress=_upload_callback(report),
            )

        directory = cache.model_dir(project_id, uploaded["item_id"], uploaded["version_id"])
        cache.prepare_sole_child_dir(directory)
        cached_path = directory / file_name
        cached_path.write_bytes(local_path.read_bytes())

        return {
            "source": {
                "connector": CONNECTOR_ID,
                "hub_id": hub_id,
                "project_id": project_id,
                "item_id": uploaded["item_id"],
            },
            "metadata": _build_metadata(uploaded),
        }


def _require_object(params: Any, name: str) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise RpcError(JSONRPC_INVALID_PARAMS, f"'{name}' must be a JSON object.")
    return params


def _require_array(params: Any, name: str) -> list[Any]:
    if not isinstance(params, list):
        raise RpcError(JSONRPC_INVALID_PARAMS, f"'{name}' must be a JSON array.")
    return params


def _require_string(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RpcError(JSONRPC_INVALID_PARAMS, f"Missing required string field '{key}'.")
    return value


def _build_metadata(version_info: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    version_number = version_info.get("version_number")
    if version_number is not None:
        metadata["revision"] = f"v{version_number}"
    last_modified = version_info.get("last_modified_time_utc")
    if isinstance(last_modified, str) and last_modified:
        metadata["date"] = last_modified
    author = version_info.get("last_modified_user_name")
    if isinstance(author, str) and author:
        metadata["author"] = author
    return metadata
