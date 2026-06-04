//! Browsing endpoints (read-only): hubs → projects → top folders → folder
//! contents → item-with-tip.

use serde_json::Value;

use super::types::{Entry, EntryType, Hub, ItemTip, Project};
use super::ApsClient;
use crate::progress::noop_auth;
use crate::rpc::RpcError;

impl ApsClient {
    fn url(&self, suffix: &str) -> String {
        format!("{}{}", self.base_url, suffix)
    }

    fn token(&self) -> Result<String, RpcError> {
        self.auth.ensure_access_token(noop_auth())
    }

    pub(crate) fn get_json(&self, url: &str) -> Result<Value, RpcError> {
        let token = self.token()?;
        let response = self
            .agent
            .get(url)
            .set("Authorization", &format!("Bearer {token}"))
            .call();
        decode_json(response, url)
    }

    pub(crate) fn post_json(&self, url: &str, payload: &Value) -> Result<Value, RpcError> {
        let token = self.token()?;
        let req = self
            .agent
            .post(url)
            .set("Authorization", &format!("Bearer {token}"))
            .set("Content-Type", "application/vnd.api+json")
            .set("Accept", "application/vnd.api+json");
        decode_json(req.send_json(payload.clone()), url)
    }

    pub fn list_hubs(&self) -> Result<Vec<Hub>, RpcError> {
        let payload = self.get_json(&self.url("/project/v1/hubs"))?;
        let mut hubs: Vec<Hub> = payload
            .get("data")
            .and_then(|v| v.as_array())
            .map(|arr| arr.iter().map(hub_from_jsonapi).collect())
            .unwrap_or_default();
        hubs.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
        Ok(hubs)
    }

    pub fn list_projects(&self, hub_id: &str) -> Result<Vec<Project>, RpcError> {
        let mut url = self.url(&format!("/project/v1/hubs/{hub_id}/projects"));
        let mut projects: Vec<Project> = Vec::new();
        loop {
            let payload = self.get_json(&url)?;
            if let Some(arr) = payload.get("data").and_then(|v| v.as_array()) {
                for item in arr {
                    projects.push(project_from_jsonapi(item));
                }
            }
            match payload.pointer("/links/next/href").and_then(|v| v.as_str()) {
                Some(next) if !next.is_empty() => url = next.to_string(),
                _ => break,
            }
        }
        projects.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
        Ok(projects)
    }

    pub fn list_top_folders(&self, hub_id: &str, project_id: &str) -> Result<Vec<Entry>, RpcError> {
        let payload = self.get_json(&self.url(&format!(
            "/project/v1/hubs/{hub_id}/projects/{project_id}/topFolders"
        )))?;
        let mut folders: Vec<Entry> = payload
            .get("data")
            .and_then(|v| v.as_array())
            .map(|arr| arr.iter().map(entry_from_jsonapi).collect())
            .unwrap_or_default();
        folders.sort_by(|a, b| a.display_name.to_lowercase().cmp(&b.display_name.to_lowercase()));
        Ok(folders)
    }

    pub fn list_folder_contents(
        &self,
        project_id: &str,
        folder_id: &str,
        object_types: &[&str],
        extension_filter: Option<&dyn Fn(&Entry) -> bool>,
    ) -> Result<Vec<Entry>, RpcError> {
        let mut url = self.url(&format!(
            "/data/v1/projects/{project_id}/folders/{folder_id}/contents"
        ));
        if !object_types.is_empty() {
            let qs: Vec<String> = object_types
                .iter()
                .map(|t| format!("filter[type]={}", url_enc(t)))
                .collect();
            url.push('?');
            url.push_str(&qs.join("&"));
        }
        let mut entries: Vec<Entry> = Vec::new();
        loop {
            let payload = self.get_json(&url)?;
            if let Some(arr) = payload.get("data").and_then(|v| v.as_array()) {
                for item in arr {
                    let entry = entry_from_jsonapi(item);
                    if entry.entry_type == EntryType::Items {
                        if let Some(filter) = extension_filter {
                            if !filter(&entry) {
                                continue;
                            }
                        }
                    }
                    entries.push(entry);
                }
            }
            match payload.pointer("/links/next/href").and_then(|v| v.as_str()) {
                Some(next) if !next.is_empty() => url = next.to_string(),
                _ => break,
            }
        }
        entries.sort_by(|a, b| a.display_name.to_lowercase().cmp(&b.display_name.to_lowercase()));
        Ok(entries)
    }

    /// Item + current tip in a single request. `hidden` reflects the
    /// soft-delete state — callers must check it before downloading.
    pub fn get_item(&self, project_id: &str, item_id: &str) -> Result<ItemTip, RpcError> {
        let payload = self.get_json(&self.url(&format!(
            "/data/v1/projects/{}/items/{}?include=tip",
            url_enc(project_id),
            url_enc(item_id),
        )))?;
        let item = payload
            .get("data")
            .cloned()
            .ok_or_else(|| RpcError::internal("Item response missing 'data'."))?;
        let item_attrs = item.get("attributes").cloned().unwrap_or_else(|| serde_json::json!({}));
        let parent_folder_id = relationship_id(&item, "parent");
        let tip_id = relationship_id(&item, "tip");
        let id = item.get("id").and_then(|v| v.as_str()).unwrap_or_default().to_string();
        let tip = payload
            .get("included")
            .and_then(|v| v.as_array())
            .and_then(|arr| {
                arr.iter()
                    .find(|inc| {
                        inc.get("type").and_then(|v| v.as_str()) == Some("versions")
                            && inc.get("id").and_then(|v| v.as_str()) == tip_id.as_deref()
                    })
                    .cloned()
            });

        let Some(tip) = tip else {
            let display = item_attrs
                .get("displayName")
                .and_then(|v| v.as_str())
                .or_else(|| item_attrs.get("name").and_then(|v| v.as_str()))
                .unwrap_or(&id)
                .to_string();
            return Ok(ItemTip {
                id,
                display_name: display,
                hidden: true,
                version_id: None,
                storage_id: None,
                version_number: None,
                last_modified_time_utc: None,
                last_modified_user_name: None,
                parent_folder_id,
            });
        };
        let tip_attrs = tip.get("attributes").cloned().unwrap_or_else(|| serde_json::json!({}));
        let display = tip_attrs
            .get("displayName")
            .and_then(|v| v.as_str())
            .or_else(|| tip_attrs.get("name").and_then(|v| v.as_str()))
            .or_else(|| item_attrs.get("displayName").and_then(|v| v.as_str()))
            .unwrap_or(&id)
            .to_string();
        Ok(ItemTip {
            id,
            display_name: display,
            hidden: item_attrs.get("hidden").and_then(|v| v.as_bool()).unwrap_or(false),
            version_id: tip.get("id").and_then(|v| v.as_str()).map(String::from),
            storage_id: relationship_id(&tip, "storage"),
            version_number: tip_attrs.get("versionNumber").cloned(),
            last_modified_time_utc: tip_attrs.get("lastModifiedTime").and_then(|v| v.as_str()).map(String::from),
            last_modified_user_name: tip_attrs.get("lastModifiedUserName").and_then(|v| v.as_str()).map(String::from),
            parent_folder_id,
        })
    }
}

fn hub_from_jsonapi(item: &Value) -> Hub {
    Hub {
        id: item.get("id").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
        name: item.pointer("/attributes/name").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
        extension_type: item
            .pointer("/attributes/extension/type")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string(),
    }
}

fn project_from_jsonapi(item: &Value) -> Project {
    Project {
        id: item.get("id").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
        name: item.pointer("/attributes/name").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
        extension_type: item
            .pointer("/attributes/extension/type")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string(),
        root_folder_id: item
            .pointer("/relationships/rootFolder/data/id")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string(),
    }
}

pub(crate) fn entry_from_jsonapi(item: &Value) -> Entry {
    let attrs = item.get("attributes").cloned().unwrap_or_else(|| serde_json::json!({}));
    let display = attrs
        .get("displayName")
        .and_then(|v| v.as_str())
        .or_else(|| attrs.get("name").and_then(|v| v.as_str()))
        .unwrap_or("")
        .to_string();
    let raw_type = item.get("type").and_then(|v| v.as_str()).unwrap_or("");
    let entry_type = match raw_type {
        "folders" => EntryType::Folders,
        "items" => EntryType::Items,
        _ => EntryType::Other,
    };
    Entry {
        id: item.get("id").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
        entry_type,
        display_name: display,
        name: attrs.get("name").and_then(|v| v.as_str()).map(String::from),
        extension_type: attrs
            .pointer("/extension/type")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
    }
}

pub(crate) fn relationship_id(data: &Value, name: &str) -> Option<String> {
    let rel = data.pointer(&format!("/relationships/{name}/data"))?;
    if let Some(obj) = rel.as_object() {
        return obj
            .get("id")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .map(String::from);
    }
    if let Some(arr) = rel.as_array() {
        return arr
            .first()
            .and_then(|x| x.get("id"))
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .map(String::from);
    }
    None
}

pub(crate) fn url_enc(s: &str) -> String {
    url::form_urlencoded::byte_serialize(s.as_bytes()).collect()
}

pub(crate) fn decode_json(
    result: Result<ureq::Response, ureq::Error>,
    url: &str,
) -> Result<Value, RpcError> {
    match result {
        Ok(resp) => resp
            .into_json::<Value>()
            .map_err(|e| RpcError::internal(format!("Response from {url} was not JSON: {e}"))),
        Err(ureq::Error::Status(code, resp)) => {
            let body = resp.into_string().unwrap_or_default();
            let msg = if body.trim().is_empty() {
                format!("HTTP {code}")
            } else {
                body.trim().to_string()
            };
            Err(RpcError::internal(msg))
        }
        Err(e) => Err(RpcError::internal(e.to_string())),
    }
}

pub(crate) fn entry_name_matches(entry: &Entry, expected: &str) -> bool {
    let target = expected.to_lowercase();
    entry.display_name.to_lowercase() == target
        || entry
            .name
            .as_deref()
            .map(|s| s.to_lowercase() == target)
            .unwrap_or(false)
}
