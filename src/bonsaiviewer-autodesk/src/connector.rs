//! Top-level connector: maps the nine JSON-RPC methods onto APS + cache + UI.

use std::cell::RefCell;
use std::path::{Path, PathBuf};
use std::rc::Rc;
use std::sync::Arc;

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use crate::aps::{ApsClient, ItemTip, UploadResult};
use crate::auth::AuthSessionService;
use crate::cache;
use crate::progress::{download_callback, upload_callback};
use crate::rpc::{Handler, RpcError};
use crate::settings as cfg;
use crate::ui::{prompt_for_filename, run_with_progress, BrowseDialog, Mode, SettingsDialog};

pub const CONNECTOR_ID: &str = "autodesk";
pub const DEFAULT_SCOPE: &str = "data:read data:write data:create";

/// Manifest written next to a cached .ifcfed. Identifies the cloud item it
/// came from so push_ifcfed can resolve the parent folder later.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    pub connector: String,
    pub hub_id: String,
    pub project_id: String,
    pub item_id: String,
    pub display_name: String,
}

/// Per-model source pointer, sent to and received from the host. Tells
/// pull_models/push_model which cloud item a local copy maps to.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Source {
    pub connector: String,
    pub hub_id: String,
    pub project_id: String,
    pub item_id: String,
}

#[derive(Debug, Deserialize)]
struct PullIfcfedParams {
    hub_id: String,
    project_id: String,
    item_id: String,
    #[serde(default)]
    display_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct PullModelEntry {
    source: Source,
    #[serde(default)]
    display_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct PushIfcfedParams {
    path: PathBuf,
    manifest: Manifest,
}

#[derive(Debug, Deserialize)]
struct PushModelParams {
    path: PathBuf,
    source: Source,
}

#[derive(Debug, Deserialize)]
struct PushInteractiveParams {
    path: PathBuf,
}

#[derive(Clone)]
struct ClientPair {
    auth: Arc<AuthSessionService>,
    aps: Arc<ApsClient>,
}

pub struct AutodeskConnector {
    inner: RefCell<Option<ClientPair>>,
}

impl AutodeskConnector {
    pub fn new() -> Self {
        let me = Self { inner: RefCell::new(None) };
        me.reload_credentials();
        me
    }

    pub fn reload_credentials(&self) {
        let client_id = cfg::load_client_id();
        if client_id.is_empty() {
            *self.inner.borrow_mut() = None;
            return;
        }
        let callback_url = format!("http://localhost:{}/", cfg::stored_callback_port());
        let auth = Arc::new(AuthSessionService::new(
            client_id,
            callback_url,
            DEFAULT_SCOPE.to_string(),
        ));
        let aps = Arc::new(ApsClient::new(auth.clone()));
        *self.inner.borrow_mut() = Some(ClientPair { auth, aps });
    }

    fn require(&self) -> Result<ClientPair, RpcError> {
        self.inner.borrow().clone().ok_or_else(|| {
            RpcError::internal(
                "Autodesk client id is not configured. Open the connector settings to set it.",
            )
        })
    }

    pub fn handlers(self: Rc<Self>) -> std::collections::HashMap<String, Handler> {
        use std::collections::HashMap;
        let mut map: HashMap<String, Handler> = HashMap::new();
        macro_rules! reg {
            ($name:literal, $method:ident) => {{
                let me = self.clone();
                map.insert($name.into(), Box::new(move |p| me.$method(p)));
            }};
        }
        reg!("pull_ifcfed_interactive", pull_ifcfed_interactive);
        reg!("pull_ifcfed", pull_ifcfed);
        reg!("pull_models", pull_models);
        reg!("pull_models_interactive", pull_models_interactive);
        reg!("push_ifcfed_interactive", push_ifcfed_interactive);
        reg!("push_ifcfed", push_ifcfed);
        reg!("push_model_interactive", push_model_interactive);
        reg!("push_model", push_model);
        reg!("open_settings", open_settings);
        map
    }

    // ---- open_settings ------------------------------------------------------

    fn open_settings(&self, _params: Value) -> Result<Value, RpcError> {
        // Capture the connector's RefCell so SettingsDialog can ask us to
        // rebuild credentials in-place after Save.
        let inner_ptr: *const RefCell<Option<ClientPair>> = &self.inner;
        // SAFETY: SettingsDialog::run blocks the calling thread, and the
        // callback fires only on this thread before run returns. The pointer
        // outlives the call because `self` is borrowed by the RPC dispatch.
        let on_reload: Arc<dyn Fn() -> Result<(), RpcError>> = Arc::new(move || {
            let cell: &RefCell<Option<ClientPair>> = unsafe { &*inner_ptr };
            let client_id = cfg::load_client_id();
            if client_id.is_empty() {
                *cell.borrow_mut() = None;
                return Ok(());
            }
            let callback_url = format!("http://localhost:{}/", cfg::stored_callback_port());
            let auth = Arc::new(AuthSessionService::new(
                client_id,
                callback_url,
                DEFAULT_SCOPE.to_string(),
            ));
            let aps = Arc::new(ApsClient::new(auth.clone()));
            *cell.borrow_mut() = Some(ClientPair { auth, aps });
            Ok(())
        });
        SettingsDialog::new(on_reload).run();
        Ok(json!({}))
    }

    // ---- pull_ifcfed_interactive -------------------------------------------

    fn pull_ifcfed_interactive(&self, _params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let chosen = BrowseDialog::new(pair.auth.clone(), pair.aps.clone(), Mode::Ifcfed).run()?;
        let entry = chosen
            .entries
            .first()
            .cloned()
            .ok_or_else(|| RpcError::internal("No entry selected."))?;
        let hub_id = chosen.hub.id.clone();
        let project_id = chosen.project.id.clone();
        let item_id = entry.id.clone();
        let display_name = entry.display_name.clone();
        let aps = pair.aps.clone();
        let path = run_with_progress("Downloading project", move |report| {
            download_ifcfed(&aps, &hub_id, &project_id, &item_id, &display_name, Some(download_callback(report, 0, 0)))
        })?;
        Ok(json!({"path": path.to_string_lossy()}))
    }

    // ---- pull_ifcfed --------------------------------------------------------

    fn pull_ifcfed(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let p: PullIfcfedParams = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("pull_ifcfed: {e}"))
        })?;
        let display = p.display_name.unwrap_or_else(|| p.item_id.clone());
        let aps = pair.aps.clone();
        let path = run_with_progress("Downloading project", move |report| {
            download_ifcfed(&aps, &p.hub_id, &p.project_id, &p.item_id, &display, Some(download_callback(report, 0, 0)))
        })?;
        Ok(json!({"path": path.to_string_lossy()}))
    }

    // ---- pull_models --------------------------------------------------------

    fn pull_models(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let entries: Vec<PullModelEntry> = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("pull_models: {e}"))
        })?;
        let total = entries.len();
        let aps = pair.aps.clone();
        let results = run_with_progress("Downloading models", move |report| {
            let mut out: Vec<Value> = Vec::with_capacity(total);
            for (index, entry) in entries.into_iter().enumerate() {
                let cb = download_callback(report.clone(), index + 1, total);
                match resolve_scripted_model(&aps, &entry, Some(cb)) {
                    Ok(Some(v)) => out.push(v),
                    Ok(None) => out.push(Value::Null),
                    Err(e) => {
                        eprintln!("pull_models[{index}] skipped: {}", e.message);
                        out.push(Value::Null);
                    }
                }
            }
            Ok::<_, RpcError>(out)
        })?;
        Ok(Value::Array(results))
    }

    // ---- pull_models_interactive --------------------------------------------

    fn pull_models_interactive(&self, _params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let chosen = BrowseDialog::new(pair.auth.clone(), pair.aps.clone(), Mode::Model).run()?;
        let total = chosen.entries.len();
        let hub = chosen.hub.clone();
        let project = chosen.project.clone();
        let aps = pair.aps.clone();
        let results = run_with_progress("Downloading models", move |report| {
            let mut out: Vec<Value> = Vec::new();
            for (index, entry) in chosen.entries.into_iter().enumerate() {
                let cb = download_callback(report.clone(), index + 1, total);
                match download_picked_model(&aps, &hub.id, &project.id, &entry.id, &entry.display_name, Some(cb)) {
                    Ok(Some(v)) => out.push(v),
                    Ok(None) => {}
                    Err(e) => eprintln!("pull_models_interactive[{index}] skipped: {}", e.message),
                }
            }
            Ok::<_, RpcError>(out)
        })?;
        Ok(Value::Array(results))
    }

    // ---- push_ifcfed_interactive --------------------------------------------

    fn push_ifcfed_interactive(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let p: PushInteractiveParams = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("push_ifcfed_interactive: {e}"))
        })?;
        check_local_exists(&p.path)?;
        let default_name = file_name_of(&p.path);
        if !default_name.to_lowercase().ends_with(".ifcfed") {
            return Err(RpcError::invalid_params("push_ifcfed_interactive expects an .ifcfed file."));
        }

        let chosen = BrowseDialog::new(pair.auth.clone(), pair.aps.clone(), Mode::Destination).run()?;
        let folder = chosen
            .entries
            .first()
            .cloned()
            .ok_or_else(|| RpcError::internal("No destination folder selected."))?;

        let raw = prompt_for_filename("Save Project", "Save .ifcfed as:", &default_name)
            .ok_or_else(|| RpcError::internal("User cancelled save to cloud."))?;
        let file_name = if raw.to_lowercase().ends_with(".ifcfed") { raw } else { format!("{raw}.ifcfed") };

        let project_id = chosen.project.id.clone();
        let folder_id = folder.id.clone();
        let aps = pair.aps.clone();
        let local_path = p.path.clone();
        let upload_name = file_name.clone();
        let uploaded = run_with_progress("Uploading project", move |report| {
            aps.upload_file_to_folder(&project_id, &folder_id, &local_path, Some(&upload_name), Some(upload_callback(report)))
        })?;

        let cached_path = cache_ifcfed_locally(&chosen.project.id, &uploaded.item_id, &file_name, &p.path)?;
        cache::write_manifest(&cached_path, &Manifest {
            connector: CONNECTOR_ID.into(),
            hub_id: chosen.hub.id,
            project_id: chosen.project.id,
            item_id: uploaded.item_id,
            display_name: file_name,
        }).map_err(|e| RpcError::internal(format!("Manifest write failed: {e}")))?;
        Ok(json!({"path": cached_path.to_string_lossy()}))
    }

    // ---- push_ifcfed --------------------------------------------------------

    fn push_ifcfed(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let p: PushIfcfedParams = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("push_ifcfed: {e}"))
        })?;
        check_local_exists(&p.path)?;
        if !file_name_of(&p.path).to_lowercase().ends_with(".ifcfed") {
            return Err(RpcError::invalid_params("push_ifcfed expects an .ifcfed file."));
        }
        if p.manifest.connector != CONNECTOR_ID {
            return Err(RpcError::invalid_params(format!("Manifest connector is not '{CONNECTOR_ID}'.")));
        }

        let item = pair.aps.get_item(&p.manifest.project_id, &p.manifest.item_id)?;
        ensure_visible(&item)?;
        let folder_id = item
            .parent_folder_id
            .clone()
            .ok_or_else(|| RpcError::internal(format!("Cannot resolve parent folder for item '{}'.", p.manifest.item_id)))?;
        let file_name = if p.manifest.display_name.is_empty() {
            item.display_name.clone()
        } else {
            p.manifest.display_name.clone()
        };

        let aps = pair.aps.clone();
        let local_path = p.path.clone();
        let project_id = p.manifest.project_id.clone();
        let upload_name = file_name.clone();
        let uploaded = run_with_progress("Uploading project", move |report| {
            aps.upload_file_to_folder(&project_id, &folder_id, &local_path, Some(&upload_name), Some(upload_callback(report)))
        })?;

        let cached_path = cache_ifcfed_locally(&p.manifest.project_id, &uploaded.item_id, &file_name, &p.path)?;
        cache::write_manifest(&cached_path, &Manifest {
            connector: CONNECTOR_ID.into(),
            hub_id: p.manifest.hub_id,
            project_id: p.manifest.project_id,
            item_id: uploaded.item_id,
            display_name: file_name,
        }).map_err(|e| RpcError::internal(format!("Manifest write failed: {e}")))?;
        Ok(json!({"path": cached_path.to_string_lossy()}))
    }

    // ---- push_model_interactive ---------------------------------------------

    fn push_model_interactive(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let p: PushInteractiveParams = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("push_model_interactive: {e}"))
        })?;
        check_local_exists(&p.path)?;

        let chosen = BrowseDialog::new(pair.auth.clone(), pair.aps.clone(), Mode::Destination).run()?;
        let folder = chosen
            .entries
            .first()
            .cloned()
            .ok_or_else(|| RpcError::internal("No destination folder selected."))?;

        let default_name = file_name_of(&p.path);
        let file_name = prompt_for_filename("Save Model", "Save model as:", &default_name)
            .ok_or_else(|| RpcError::internal("User cancelled save to cloud."))?;

        let project_id = chosen.project.id.clone();
        let folder_id = folder.id.clone();
        let aps = pair.aps.clone();
        let local_path = p.path.clone();
        let upload_name = file_name.clone();
        let uploaded = run_with_progress("Uploading model", move |report| {
            aps.upload_file_to_folder(&project_id, &folder_id, &local_path, Some(&upload_name), Some(upload_callback(report)))
        })?;

        let cached_path = cache_model_locally(&chosen.project.id, &uploaded.item_id, &uploaded.version_id, &file_name, &p.path)?;
        Ok(json!({
            "display_name": file_name,
            "path": cached_path.to_string_lossy(),
            "source": Source {
                connector: CONNECTOR_ID.into(),
                hub_id: chosen.hub.id,
                project_id: chosen.project.id,
                item_id: uploaded.item_id.clone(),
            },
            "metadata": build_metadata_from_upload(&uploaded),
        }))
    }

    // ---- push_model ---------------------------------------------------------

    fn push_model(&self, params: Value) -> Result<Value, RpcError> {
        let pair = self.require()?;
        let p: PushModelParams = serde_json::from_value(params).map_err(|e| {
            RpcError::invalid_params(format!("push_model: {e}"))
        })?;
        check_local_exists(&p.path)?;
        if p.source.connector != CONNECTOR_ID {
            return Err(RpcError::invalid_params(format!("Source connector is not '{CONNECTOR_ID}'.")));
        }

        let item = pair.aps.get_item(&p.source.project_id, &p.source.item_id)?;
        ensure_visible(&item)?;
        let folder_id = item
            .parent_folder_id
            .clone()
            .ok_or_else(|| RpcError::internal(format!("Cannot resolve parent folder for item '{}'.", p.source.item_id)))?;
        let file_name = if item.display_name.is_empty() { file_name_of(&p.path) } else { item.display_name.clone() };

        let aps = pair.aps.clone();
        let local_path = p.path.clone();
        let project_id = p.source.project_id.clone();
        let upload_name = file_name.clone();
        let uploaded = run_with_progress("Uploading model", move |report| {
            aps.upload_file_to_folder(&project_id, &folder_id, &local_path, Some(&upload_name), Some(upload_callback(report)))
        })?;

        let _cached_path = cache_model_locally(&p.source.project_id, &uploaded.item_id, &uploaded.version_id, &file_name, &p.path)?;
        Ok(json!({
            "source": Source {
                connector: CONNECTOR_ID.into(),
                hub_id: p.source.hub_id,
                project_id: p.source.project_id,
                item_id: uploaded.item_id.clone(),
            },
            "metadata": build_metadata_from_upload(&uploaded),
        }))
    }
}

// ---- shared helpers --------------------------------------------------------

fn download_ifcfed(
    aps: &ApsClient,
    hub_id: &str,
    project_id: &str,
    item_id: &str,
    display_name_hint: &str,
    progress: Option<crate::progress::ApsProgress>,
) -> Result<PathBuf, RpcError> {
    let item = aps.get_item(project_id, item_id)?;
    ensure_visible(&item)?;
    let storage_id = item
        .storage_id
        .clone()
        .ok_or_else(|| RpcError::internal(format!("Autodesk item '{item_id}' has no downloadable storage.")))?;
    let file_name = if !item.display_name.is_empty() {
        item.display_name.clone()
    } else if !display_name_hint.is_empty() {
        display_name_hint.to_string()
    } else {
        item_id.to_string()
    };
    if !file_name.to_lowercase().ends_with(".ifcfed") {
        return Err(RpcError::internal(format!("Item '{file_name}' is not an .ifcfed file.")));
    }
    let directory = cache::prepare_sole_child_dir(&cache::ifcfed_dir(project_id, item_id))
        .map_err(|e| RpcError::internal(format!("Cache dir prep failed: {e}")))?;
    let ifcfed_path = directory.join(&file_name);
    aps.download_storage_to_file(&storage_id, &ifcfed_path, progress)?;
    cache::write_manifest(&ifcfed_path, &Manifest {
        connector: CONNECTOR_ID.into(),
        hub_id: hub_id.into(),
        project_id: project_id.into(),
        item_id: item_id.into(),
        display_name: file_name,
    }).map_err(|e| RpcError::internal(format!("Manifest write failed: {e}")))?;
    Ok(ifcfed_path)
}

fn resolve_scripted_model(
    aps: &ApsClient,
    entry: &PullModelEntry,
    progress: Option<crate::progress::ApsProgress>,
) -> Result<Option<Value>, RpcError> {
    if entry.source.connector != CONNECTOR_ID {
        return Err(RpcError::invalid_params(format!("Source connector is not '{CONNECTOR_ID}'.")));
    }
    let display_hint = entry
        .display_name
        .clone()
        .unwrap_or_else(|| entry.source.item_id.clone());

    let item = aps.get_item(&entry.source.project_id, &entry.source.item_id)?;
    if item.hidden {
        eprintln!("Autodesk item '{}' is hidden/deleted; returning null.", entry.source.item_id);
        return Ok(None);
    }
    let storage_id = item
        .storage_id
        .clone()
        .ok_or_else(|| RpcError::internal(format!("Autodesk item '{}' has no downloadable storage.", entry.source.item_id)))?;
    let file_name = if item.display_name.is_empty() { display_hint } else { item.display_name.clone() };
    let version_id = item.version_id.clone().unwrap_or_default();

    let directory = cache::model_dir(&entry.source.project_id, &entry.source.item_id, &version_id);
    let model_path = directory.join(&file_name);
    if !model_path.exists() {
        cache::prepare_sole_child_dir(&directory)
            .map_err(|e| RpcError::internal(format!("Cache dir prep failed: {e}")))?;
        aps.download_storage_to_file(&storage_id, &model_path, progress)?;
    }
    Ok(Some(json!({
        "path": model_path.to_string_lossy(),
        "metadata": build_metadata_from_item(&item),
    })))
}

fn download_picked_model(
    aps: &ApsClient,
    hub_id: &str,
    project_id: &str,
    entry_id: &str,
    entry_display: &str,
    progress: Option<crate::progress::ApsProgress>,
) -> Result<Option<Value>, RpcError> {
    let item = aps.get_item(project_id, entry_id)?;
    ensure_visible(&item)?;
    let storage_id = item
        .storage_id
        .clone()
        .ok_or_else(|| RpcError::internal(format!("Autodesk item '{entry_id}' has no downloadable storage.")))?;
    let file_name = if !item.display_name.is_empty() {
        item.display_name.clone()
    } else if !entry_display.is_empty() {
        entry_display.to_string()
    } else {
        entry_id.to_string()
    };
    let version_id = item.version_id.clone().unwrap_or_default();

    let directory = cache::model_dir(project_id, entry_id, &version_id);
    let model_path = directory.join(&file_name);
    if !model_path.exists() {
        cache::prepare_sole_child_dir(&directory)
            .map_err(|e| RpcError::internal(format!("Cache dir prep failed: {e}")))?;
        aps.download_storage_to_file(&storage_id, &model_path, progress)?;
    }

    Ok(Some(json!({
        "display_name": file_name,
        "source": Source {
            connector: CONNECTOR_ID.into(),
            hub_id: hub_id.into(),
            project_id: project_id.into(),
            item_id: entry_id.into(),
        },
        "path": model_path.to_string_lossy(),
        "metadata": build_metadata_from_item(&item),
    })))
}

fn cache_ifcfed_locally(project_id: &str, item_id: &str, file_name: &str, src: &Path) -> Result<PathBuf, RpcError> {
    let directory = cache::prepare_sole_child_dir(&cache::ifcfed_dir(project_id, item_id))
        .map_err(|e| RpcError::internal(format!("Cache dir prep failed: {e}")))?;
    let cached_path = directory.join(file_name);
    std::fs::copy(src, &cached_path).map_err(|e| RpcError::internal(format!("Cache copy failed: {e}")))?;
    Ok(cached_path)
}

fn cache_model_locally(project_id: &str, item_id: &str, version_id: &str, file_name: &str, src: &Path) -> Result<PathBuf, RpcError> {
    let directory = cache::model_dir(project_id, item_id, version_id);
    cache::prepare_sole_child_dir(&directory)
        .map_err(|e| RpcError::internal(format!("Cache dir prep failed: {e}")))?;
    let cached_path = directory.join(file_name);
    std::fs::copy(src, &cached_path).map_err(|e| RpcError::internal(format!("Cache copy failed: {e}")))?;
    Ok(cached_path)
}

fn build_metadata_from_item(item: &ItemTip) -> Value {
    let mut metadata = serde_json::Map::new();
    if let Some(v) = &item.version_number {
        if !v.is_null() {
            metadata.insert("revision".into(), json!(format!("v{}", json_value_to_display(v))));
        }
    }
    if let Some(s) = &item.last_modified_time_utc {
        if !s.is_empty() {
            metadata.insert("date".into(), json!(s));
        }
    }
    if let Some(s) = &item.last_modified_user_name {
        if !s.is_empty() {
            metadata.insert("author".into(), json!(s));
        }
    }
    Value::Object(metadata)
}

fn build_metadata_from_upload(uploaded: &UploadResult) -> Value {
    let mut metadata = serde_json::Map::new();
    if let Some(v) = &uploaded.version_number {
        if !v.is_null() {
            metadata.insert("revision".into(), json!(format!("v{}", json_value_to_display(v))));
        }
    }
    if let Some(s) = &uploaded.last_modified_time_utc {
        if !s.is_empty() {
            metadata.insert("date".into(), json!(s));
        }
    }
    if let Some(s) = &uploaded.last_modified_user_name {
        if !s.is_empty() {
            metadata.insert("author".into(), json!(s));
        }
    }
    Value::Object(metadata)
}

fn json_value_to_display(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        Value::Bool(b) => b.to_string(),
        _ => String::new(),
    }
}

fn ensure_visible(item: &ItemTip) -> Result<(), RpcError> {
    if item.hidden {
        return Err(RpcError::internal(format!("Autodesk item '{}' has been deleted.", item.id)));
    }
    Ok(())
}

fn check_local_exists(path: &Path) -> Result<(), RpcError> {
    if !path.exists() {
        return Err(RpcError::invalid_params(format!("Local file '{}' does not exist.", path.display())));
    }
    Ok(())
}

fn file_name_of(path: &Path) -> String {
    path.file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The host attaches a top-level "id" we don't consume; serde should
    /// ignore unknown fields rather than fail the whole batch.
    #[test]
    fn pull_model_entry_ignores_extra_fields() {
        let json = serde_json::json!({
            "id": "abc",
            "display_name": "bar.ifc",
            "source": {"connector": "autodesk", "hub_id": "h", "project_id": "p", "item_id": "i"}
        });
        let entry: PullModelEntry = serde_json::from_value(json).unwrap();
        assert_eq!(entry.display_name.as_deref(), Some("bar.ifc"));
    }
}
