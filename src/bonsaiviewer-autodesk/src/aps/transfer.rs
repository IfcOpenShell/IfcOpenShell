//! Download (signed S3 GET) and upload (signed S3 multi-part PUT + complete).

use std::cmp::min;
use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;

use serde_json::{json, Value};

use super::browse::{decode_json, entry_name_matches, url_enc};
use super::types::UploadResult;
use super::ApsClient;
use crate::progress::ApsProgress;
use crate::rpc::RpcError;

const CHUNK_SIZE: u64 = 5 * 1024 * 1024;
const PARTS_PER_BATCH: u32 = 5;
const READ_BUF: usize = 64 * 1024;

impl ApsClient {
    pub fn download_storage_to_file(
        &self,
        storage_id: &str,
        destination: &Path,
        progress: Option<ApsProgress>,
    ) -> Result<(), RpcError> {
        let (bucket, object) = parse_storage_id(storage_id)?;
        let signed_url = self.get_signed_download_url(&bucket, &object)?;
        self.download_to_file(&signed_url, destination, progress)
    }

    pub fn upload_file_to_folder(
        &self,
        project_id: &str,
        folder_id: &str,
        local_path: &Path,
        display_name: Option<&str>,
        progress: Option<ApsProgress>,
    ) -> Result<UploadResult, RpcError> {
        if !local_path.exists() {
            return Err(RpcError::internal(format!(
                "Local file '{}' does not exist.",
                local_path.display()
            )));
        }
        let file_name = display_name.map(str::to_string).unwrap_or_else(|| {
            local_path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned()
        });
        let storage_id = self.create_storage(project_id, folder_id, &file_name)?;
        let (bucket, object) = parse_storage_id(&storage_id)?;
        self.upload_local_file_to_oss(&bucket, &object, local_path, progress)?;
        if let Some(existing) = self.find_item_in_folder(project_id, folder_id, &file_name)? {
            self.create_version(project_id, &existing, &file_name, &storage_id)
        } else {
            self.create_item(project_id, folder_id, &file_name, &storage_id)
        }
    }

    fn get_signed_download_url(&self, bucket: &str, object: &str) -> Result<String, RpcError> {
        let payload = self.get_json(&format!(
            "{}/oss/v2/buckets/{}/objects/{}/signeds3download",
            self.base_url,
            url_enc(bucket),
            url_enc(object),
        ))?;
        payload
            .get("url")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .map(String::from)
            .ok_or_else(|| {
                RpcError::internal("Signed download URL response did not contain a URL.")
            })
    }

    fn download_to_file(
        &self,
        url: &str,
        destination: &Path,
        progress: Option<ApsProgress>,
    ) -> Result<(), RpcError> {
        let resp = match self.agent.get(url).call() {
            Ok(r) => r,
            Err(ureq::Error::Status(code, resp)) => {
                let body = resp.into_string().unwrap_or_default();
                let msg = if body.trim().is_empty() {
                    format!("HTTP {code}")
                } else {
                    body.trim().to_string()
                };
                return Err(RpcError::internal(msg));
            }
            Err(e) => return Err(RpcError::internal(e.to_string())),
        };
        let total_bytes: Option<u64> = resp.header("Content-Length").and_then(|s| s.parse().ok());
        let name = destination
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        let mut reader = resp.into_reader();
        let mut file = File::create(destination).map_err(|e| {
            RpcError::internal(format!("Cannot create '{}': {e}", destination.display()))
        })?;
        let mut buf = vec![0u8; READ_BUF];
        let mut downloaded: u64 = 0;
        loop {
            let n = reader
                .read(&mut buf)
                .map_err(|e| RpcError::internal(format!("Download read failed: {e}")))?;
            if n == 0 {
                break;
            }
            file.write_all(&buf[..n])
                .map_err(|e| RpcError::internal(format!("Download write failed: {e}")))?;
            downloaded += n as u64;
            if let Some(cb) = &progress {
                let percent =
                    total_bytes.map(|t| min(100, ((downloaded as f64 / t as f64) * 100.0) as i32));
                cb(&name, percent, Some(downloaded), total_bytes);
            }
        }
        Ok(())
    }

    fn create_storage(
        &self,
        project_id: &str,
        folder_id: &str,
        file_name: &str,
    ) -> Result<String, RpcError> {
        let payload = self.post_json(
            &format!(
                "{}/data/v1/projects/{}/storage",
                self.base_url,
                url_enc(project_id)
            ),
            &json!({
                "jsonapi": {"version": "1.0"},
                "data": {
                    "type": "objects",
                    "attributes": {"name": file_name},
                    "relationships": {"target": {"data": {"type": "folders", "id": folder_id}}},
                },
            }),
        )?;
        payload
            .pointer("/data/id")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .map(String::from)
            .ok_or_else(|| RpcError::internal("Storage creation did not return an object id."))
    }

    fn upload_local_file_to_oss(
        &self,
        bucket: &str,
        object: &str,
        local_path: &Path,
        progress: Option<ApsProgress>,
    ) -> Result<(), RpcError> {
        let file_size = std::fs::metadata(local_path)
            .map_err(|e| RpcError::internal(format!("stat '{}': {e}", local_path.display())))?
            .len();
        let total_parts = file_size.div_ceil(CHUNK_SIZE).max(1);
        let file_name = local_path
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();

        let mut handle = File::open(local_path)
            .map_err(|e| RpcError::internal(format!("open '{}': {e}", local_path.display())))?;
        let mut upload_key: Option<String> = None;
        let mut parts_uploaded: u64 = 0;
        let mut bytes_uploaded: u64 = 0;
        let mut chunk = vec![0u8; CHUNK_SIZE as usize];

        while parts_uploaded < total_parts {
            let parts_to_request = min(total_parts - parts_uploaded, PARTS_PER_BATCH as u64) as u32;
            let first_part = (parts_uploaded + 1) as u32;
            let signed = self.get_signed_upload_urls(
                bucket,
                object,
                upload_key.as_deref(),
                first_part,
                parts_to_request,
            )?;
            if upload_key.is_none() {
                upload_key = signed
                    .get("uploadKey")
                    .and_then(|v| v.as_str())
                    .map(String::from);
            }
            let urls = signed
                .get("urls")
                .and_then(|v| v.as_array())
                .filter(|a| !a.is_empty())
                .ok_or_else(|| {
                    RpcError::internal("Upload URL response did not contain upload URLs.")
                })?
                .clone();
            for url in &urls {
                if parts_uploaded >= total_parts {
                    break;
                }
                let url_str = url
                    .as_str()
                    .ok_or_else(|| RpcError::internal("Upload URL was not a string."))?;
                let n = fill(&mut handle, &mut chunk)
                    .map_err(|e| RpcError::internal(format!("Upload read failed: {e}")))?;
                if n == 0 {
                    break;
                }
                self.put_bytes(url_str, &chunk[..n])?;
                parts_uploaded += 1;
                bytes_uploaded += n as u64;
                if let Some(cb) = &progress {
                    let percent = if file_size == 0 {
                        100
                    } else {
                        min(
                            100,
                            ((bytes_uploaded as f64 / file_size as f64) * 100.0) as i32,
                        )
                    };
                    cb(
                        &file_name,
                        Some(percent),
                        Some(bytes_uploaded),
                        Some(file_size),
                    );
                }
            }
        }

        let key =
            upload_key.ok_or_else(|| RpcError::internal("Upload did not return an upload key."))?;
        self.complete_signed_upload(bucket, object, &key)
    }

    fn get_signed_upload_urls(
        &self,
        bucket: &str,
        object: &str,
        upload_key: Option<&str>,
        first_part: u32,
        parts: u32,
    ) -> Result<Value, RpcError> {
        let token = self
            .auth
            .ensure_access_token(crate::progress::noop_auth())?;
        let mut url = format!(
            "{}/oss/v2/buckets/{}/objects/{}/signeds3upload?minutesExpiration=10&firstPart={}&parts={}",
            self.base_url,
            url_enc(bucket),
            url_enc(object),
            first_part,
            parts,
        );
        if let Some(k) = upload_key {
            url.push_str(&format!("&uploadKey={}", url_enc(k)));
        }
        let resp = self
            .agent
            .get(&url)
            .set("Authorization", &format!("Bearer {token}"))
            .call();
        decode_json(resp, &url)
    }

    fn complete_signed_upload(
        &self,
        bucket: &str,
        object: &str,
        upload_key: &str,
    ) -> Result<(), RpcError> {
        let token = self
            .auth
            .ensure_access_token(crate::progress::noop_auth())?;
        let url = format!(
            "{}/oss/v2/buckets/{}/objects/{}/signeds3upload",
            self.base_url,
            url_enc(bucket),
            url_enc(object),
        );
        match self
            .agent
            .post(&url)
            .set("Authorization", &format!("Bearer {token}"))
            .set("Content-Type", "application/json")
            .send_json(json!({"uploadKey": upload_key}))
        {
            Ok(_) => Ok(()),
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

    fn put_bytes(&self, url: &str, content: &[u8]) -> Result<(), RpcError> {
        match self
            .agent
            .put(url)
            .set("Content-Type", "application/octet-stream")
            .send_bytes(content)
        {
            Ok(_) => Ok(()),
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

    fn find_item_in_folder(
        &self,
        project_id: &str,
        folder_id: &str,
        file_name: &str,
    ) -> Result<Option<String>, RpcError> {
        let children = self.list_folder_contents(project_id, folder_id, &["items"], None)?;
        Ok(children
            .into_iter()
            .find(|c| entry_name_matches(c, file_name))
            .map(|c| c.id))
    }

    fn create_version(
        &self,
        project_id: &str,
        item_id: &str,
        file_name: &str,
        storage_id: &str,
    ) -> Result<UploadResult, RpcError> {
        let payload = self.post_json(
            &format!(
                "{}/data/v1/projects/{}/versions",
                self.base_url,
                url_enc(project_id)
            ),
            &json!({
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
            }),
        )?;
        let version = payload
            .get("data")
            .ok_or_else(|| RpcError::internal("Create version response missing 'data'."))?;
        let attrs = version
            .get("attributes")
            .cloned()
            .unwrap_or_else(|| json!({}));
        Ok(UploadResult {
            item_id: item_id.to_string(),
            version_id: version
                .get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            display_name: file_name.to_string(),
            version_number: attrs.get("versionNumber").cloned(),
            last_modified_time_utc: attrs
                .get("lastModifiedTime")
                .and_then(|v| v.as_str())
                .map(String::from),
            last_modified_user_name: attrs
                .get("lastModifiedUserName")
                .and_then(|v| v.as_str())
                .map(String::from),
        })
    }

    fn create_item(
        &self,
        project_id: &str,
        folder_id: &str,
        file_name: &str,
        storage_id: &str,
    ) -> Result<UploadResult, RpcError> {
        let payload = self.post_json(
            &format!(
                "{}/data/v1/projects/{}/items",
                self.base_url,
                url_enc(project_id)
            ),
            &json!({
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
                "included": [{
                    "type": "versions",
                    "id": "1",
                    "attributes": {
                        "name": file_name,
                        "extension": {"type": "versions:autodesk.bim360:File", "version": "1.0"},
                    },
                    "relationships": {"storage": {"data": {"type": "objects", "id": storage_id}}},
                }],
            }),
        )?;
        let item = payload
            .get("data")
            .ok_or_else(|| RpcError::internal("Create item response missing 'data'."))?;
        let item_id = item
            .get("id")
            .and_then(|v| v.as_str())
            .ok_or_else(|| RpcError::internal("Create item response missing item id."))?
            .to_string();
        let mut version_id = "1".to_string();
        let mut version_number: Option<Value> = Some(json!(1));
        let mut last_modified_time: Option<String> = None;
        let mut last_modified_user: Option<String> = None;
        if let Some(included) = payload.get("included").and_then(|v| v.as_array()) {
            if let Some(ver) = included
                .iter()
                .find(|i| i.get("type").and_then(|t| t.as_str()) == Some("versions"))
            {
                if let Some(id) = ver.get("id").and_then(|v| v.as_str()) {
                    version_id = id.to_string();
                }
                if let Some(attrs) = ver.get("attributes") {
                    if let Some(v) = attrs.get("versionNumber") {
                        version_number = Some(v.clone());
                    }
                    last_modified_time = attrs
                        .get("lastModifiedTime")
                        .and_then(|v| v.as_str())
                        .map(String::from);
                    last_modified_user = attrs
                        .get("lastModifiedUserName")
                        .and_then(|v| v.as_str())
                        .map(String::from);
                }
            }
        }
        Ok(UploadResult {
            item_id,
            version_id,
            display_name: file_name.to_string(),
            version_number,
            last_modified_time_utc: last_modified_time,
            last_modified_user_name: last_modified_user,
        })
    }
}

pub(crate) fn parse_storage_id(storage_id: &str) -> Result<(String, String), RpcError> {
    let marker = "urn:adsk.objects:os.object:";
    let path = storage_id.strip_prefix(marker).ok_or_else(|| {
        RpcError::internal(format!("Unsupported storage identifier '{storage_id}'."))
    })?;
    let slash = path.find('/').ok_or_else(|| {
        RpcError::internal(format!("Malformed storage identifier '{storage_id}'."))
    })?;
    if slash == 0 || slash == path.len() - 1 {
        return Err(RpcError::internal(format!(
            "Malformed storage identifier '{storage_id}'."
        )));
    }
    Ok((path[..slash].to_string(), path[slash + 1..].to_string()))
}

fn fill(file: &mut File, buf: &mut [u8]) -> std::io::Result<usize> {
    let mut filled = 0;
    while filled < buf.len() {
        let n = file.read(&mut buf[filled..])?;
        if n == 0 {
            break;
        }
        filled += n;
    }
    Ok(filled)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_storage_id() {
        let (bucket, object) =
            parse_storage_id("urn:adsk.objects:os.object:wip.dm.prod/abc.ifc").unwrap();
        assert_eq!(bucket, "wip.dm.prod");
        assert_eq!(object, "abc.ifc");
    }

    #[test]
    fn rejects_bad_storage_id() {
        assert!(parse_storage_id("nope").is_err());
        assert!(parse_storage_id("urn:adsk.objects:os.object:nobucket").is_err());
        assert!(parse_storage_id("urn:adsk.objects:os.object:/noobject").is_err());
    }
}
