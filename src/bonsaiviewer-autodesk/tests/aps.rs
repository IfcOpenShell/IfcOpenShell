//! Integration test: drive ApsClient end-to-end against a local TCP server
//! that serves canned APS responses.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use chrono::{Duration as ChronoDuration, Utc};

use bonsaiviewer_autodesk::aps::{ApsClient, EntryType};
use bonsaiviewer_autodesk::auth::{AuthBuilder, InMemoryTokenStore, StoredToken};
use bonsaiviewer_autodesk::progress::noop_auth;

/// Canned reply: a Vec of (method, path-prefix) → status + body. The stub
/// matches the request against the first entry whose method matches and whose
/// path starts with the prefix, then pops it so the next request uses the
/// next entry (call-order matters in our tests).
struct StubServer {
    base_url: String,
    handle: Option<thread::JoinHandle<()>>,
}

impl Drop for StubServer {
    fn drop(&mut self) {
        if let Some(h) = self.handle.take() {
            // Best effort: the server thread exits on TCP error when the test
            // tears down. Don't block tests on join.
            drop(h);
        }
    }
}

fn spawn_stub(routes: Vec<(&'static str, &'static str, u16, String)>) -> StubServer {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    let mut routes = routes;
    let handle = thread::spawn(move || {
        for incoming in listener.incoming() {
            let Ok(mut stream) = incoming else { return };
            stream.set_read_timeout(Some(Duration::from_secs(5))).ok();
            stream.set_write_timeout(Some(Duration::from_secs(5))).ok();

            // Read request line + headers.
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut request_line = String::new();
            if reader.read_line(&mut request_line).unwrap_or(0) == 0 {
                return;
            }
            let mut content_length: usize = 0;
            loop {
                let mut h = String::new();
                if reader.read_line(&mut h).unwrap_or(0) == 0 {
                    break;
                }
                if h == "\r\n" || h == "\n" {
                    break;
                }
                if let Some(v) = h
                    .strip_prefix("Content-Length: ")
                    .or_else(|| h.strip_prefix("content-length: "))
                {
                    content_length = v.trim().parse().unwrap_or(0);
                }
            }
            // Drain the body so the client doesn't choke on a half-read socket
            // when we send our reply and close.
            if content_length > 0 {
                let mut body = vec![0u8; content_length];
                let _ = reader.read_exact(&mut body);
            }

            let parts: Vec<&str> = request_line.split_whitespace().collect();
            let method = parts.first().copied().unwrap_or("");
            let path = parts.get(1).copied().unwrap_or("/");

            let idx = routes
                .iter()
                .position(|(m, p, _, _)| *m == method && path.starts_with(p));
            let (status, body) = match idx {
                Some(i) => {
                    let (_, _, status, body) = routes.remove(i);
                    (status, body)
                }
                None => (404, format!("no route for {method} {path}")),
            };
            let header = format!(
                "HTTP/1.1 {} {}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                status,
                status_text(status),
                body.len()
            );
            let _ = stream.write_all(header.as_bytes());
            let _ = stream.write_all(body.as_bytes());
            let _ = stream.flush();
        }
    });
    StubServer {
        base_url: format!("http://127.0.0.1:{port}"),
        handle: Some(handle),
    }
}

fn status_text(code: u16) -> &'static str {
    match code {
        200 => "OK",
        201 => "Created",
        204 => "No Content",
        404 => "Not Found",
        _ => "OK",
    }
}

fn auth_with_valid_token() -> AuthBuilder {
    let token = StoredToken {
        client_id: "test".into(),
        access_token: "AT".into(),
        refresh_token: "RT".into(),
        access_token_expires_at: Utc::now() + ChronoDuration::hours(1),
        refresh_token_expires_at: Utc::now() + ChronoDuration::hours(24),
        scope: "data:read data:write data:create".into(),
    };
    AuthBuilder::new(
        "test".into(),
        "http://127.0.0.1:9999/".into(),
        "data:read data:write data:create".into(),
        Box::new(InMemoryTokenStore::preloaded(token)),
    )
}

fn make_client(base_url: String) -> ApsClient {
    let auth = Arc::new(auth_with_valid_token().build());
    // Quick sanity check that ensure_access_token returns the cached token.
    assert_eq!(auth.ensure_access_token(noop_auth()).unwrap(), "AT");
    ApsClient::with_base_url(auth, base_url)
}

#[test]
fn list_hubs_decodes_and_sorts() {
    let body = r#"{
        "data": [
            {"id": "h2", "type": "hubs", "attributes": {"name": "Beta", "extension": {"type": "hubs:autodesk.bim360:Account"}}},
            {"id": "h1", "type": "hubs", "attributes": {"name": "alpha", "extension": {"type": "hubs:autodesk.core:Hub"}}}
        ]
    }"#;
    let server = spawn_stub(vec![("GET", "/project/v1/hubs", 200, body.into())]);
    let client = make_client(server.base_url.clone());
    let hubs = client.list_hubs().unwrap();
    assert_eq!(hubs.len(), 2);
    assert_eq!(hubs[0].name, "alpha");
    assert_eq!(hubs[1].name, "Beta");
}

#[test]
fn list_folder_contents_filters_ifcfed() {
    let body = r#"{
        "data": [
            {"id": "f1", "type": "folders", "attributes": {"displayName": "sub"}},
            {"id": "i1", "type": "items", "attributes": {"displayName": "model.ifc"}},
            {"id": "i2", "type": "items", "attributes": {"displayName": "model.ifcfed"}}
        ]
    }"#;
    let server = spawn_stub(vec![(
        "GET",
        "/data/v1/projects/P/folders/F/contents",
        200,
        body.into(),
    )]);
    let client = make_client(server.base_url.clone());
    let filter =
        |e: &bonsaiviewer_autodesk::aps::Entry| e.display_name.to_lowercase().ends_with(".ifcfed");
    let entries = client
        .list_folder_contents("P", "F", &["folders", "items"], Some(&filter))
        .unwrap();
    // Folders bypass the filter; only ifcfed items are kept.
    let names: Vec<_> = entries.iter().map(|e| e.display_name.clone()).collect();
    assert_eq!(names, vec!["model.ifcfed".to_string(), "sub".to_string()]);
}

#[test]
fn get_item_returns_tip_metadata() {
    let body = r#"{
        "data": {
            "id": "I",
            "type": "items",
            "attributes": {"displayName": "model.ifc", "hidden": false},
            "relationships": {
                "tip": {"data": {"type": "versions", "id": "V"}},
                "parent": {"data": {"type": "folders", "id": "F"}}
            }
        },
        "included": [{
            "id": "V",
            "type": "versions",
            "attributes": {
                "displayName": "model.ifc",
                "versionNumber": 3,
                "lastModifiedTime": "2025-01-01T00:00:00Z",
                "lastModifiedUserName": "alice"
            },
            "relationships": {
                "storage": {"data": {"type": "objects", "id": "urn:adsk.objects:os.object:bk/obj"}}
            }
        }]
    }"#;
    let server = spawn_stub(vec![(
        "GET",
        "/data/v1/projects/P/items/I",
        200,
        body.into(),
    )]);
    let client = make_client(server.base_url.clone());
    let item = client.get_item("P", "I").unwrap();
    assert!(!item.hidden);
    assert_eq!(item.version_id.as_deref(), Some("V"));
    assert_eq!(
        item.storage_id.as_deref(),
        Some("urn:adsk.objects:os.object:bk/obj")
    );
    assert_eq!(item.last_modified_user_name.as_deref(), Some("alice"));
    assert_eq!(item.parent_folder_id.as_deref(), Some("F"));
}

#[test]
fn get_item_handles_missing_tip_as_hidden() {
    let body = r#"{
        "data": {
            "id": "I",
            "type": "items",
            "attributes": {"displayName": "deleted.ifc", "hidden": true},
            "relationships": {
                "tip": {"data": {"type": "versions", "id": "missing"}},
                "parent": {"data": {"type": "folders", "id": "F"}}
            }
        }
    }"#;
    let server = spawn_stub(vec![(
        "GET",
        "/data/v1/projects/P/items/I",
        200,
        body.into(),
    )]);
    let client = make_client(server.base_url.clone());
    let item = client.get_item("P", "I").unwrap();
    assert!(item.hidden);
    assert!(item.storage_id.is_none());
    assert!(item.version_id.is_none());
}

#[test]
fn download_signed_then_get_writes_file() {
    let tmp = tempfile::tempdir().unwrap();
    let dst = tmp.path().join("out.bin");
    let signed = format!(r#"{{"url": "{base}/payload"}}"#, base = "PLACEHOLDER");
    // We need two-stage: first signed url returns a pointer into the same
    // stub, then the GET against that path returns the bytes.
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    let base = format!("http://127.0.0.1:{port}");
    let signed_with_url = signed.replace("PLACEHOLDER", &base);
    let payload_bytes = b"hello-bytes-12345";
    let mut routes: Vec<(&'static str, &'static str, u16, String)> = vec![
        (
            "GET",
            "/oss/v2/buckets/bk/objects/obj/signeds3download",
            200,
            signed_with_url,
        ),
        (
            "GET",
            "/payload",
            200,
            String::from_utf8(payload_bytes.to_vec()).unwrap(),
        ),
    ];
    // Hand-roll a stub on the bound listener so we can re-use the same port.
    let handle = thread::spawn(move || {
        for _ in 0..2 {
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut request_line = String::new();
            reader.read_line(&mut request_line).unwrap();
            loop {
                let mut h = String::new();
                if reader.read_line(&mut h).unwrap_or(0) == 0 {
                    break;
                }
                if h == "\r\n" || h == "\n" {
                    break;
                }
            }
            let parts: Vec<&str> = request_line.split_whitespace().collect();
            let method = parts[0];
            let path = parts[1];
            let idx = routes
                .iter()
                .position(|(m, p, _, _)| *m == method && path.starts_with(p))
                .unwrap();
            let (_, _, status, body) = routes.remove(idx);
            let header = format!(
                "HTTP/1.1 {status} OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                body.len()
            );
            let _ = stream.write_all(header.as_bytes());
            let _ = stream.write_all(body.as_bytes());
            let _ = stream.flush();
        }
    });
    let client = make_client(base);
    client
        .download_storage_to_file("urn:adsk.objects:os.object:bk/obj", &dst, None)
        .unwrap();
    handle.join().unwrap();
    let read = std::fs::read(&dst).unwrap();
    assert_eq!(read, payload_bytes);
}

#[test]
fn upload_small_file_creates_new_item() {
    use std::cell::Cell;

    let tmp = tempfile::tempdir().unwrap();
    let src = tmp.path().join("model.ifc");
    std::fs::write(&src, b"local file contents").unwrap();

    // Sequence: create_storage → signed_upload (presigned URL list) → PUT
    // bytes → complete_signed_upload → list folder (no existing) →
    // create_item.
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    let base = format!("http://127.0.0.1:{port}");
    let presigned_url = format!("{base}/presigned/0");

    let put_bytes_received: Arc<std::sync::Mutex<Vec<u8>>> =
        Arc::new(std::sync::Mutex::new(Vec::new()));
    let put_bytes_clone = put_bytes_received.clone();

    let create_storage_body =
        r#"{"data":{"id":"urn:adsk.objects:os.object:bk/obj","type":"objects"}}"#.to_string();
    let signed_upload_body = format!(r#"{{"uploadKey":"UK1","urls":["{presigned_url}"]}}"#);
    let complete_body = r#"{}"#.to_string();
    let folder_contents_body = r#"{"data":[]}"#.to_string();
    let create_item_body = r#"{
        "data": {"id":"NEW_ITEM","type":"items"},
        "included": [{"id":"V1","type":"versions","attributes":{"versionNumber":1,"lastModifiedTime":"2025-01-01T00:00:00Z","lastModifiedUserName":"bob"}}]
    }"#.to_string();

    let put_seen = Cell::new(false);
    let _ = put_seen;

    let handle = thread::spawn(move || {
        let expected = vec![
            ("POST", "/data/v1/projects/P/storage", create_storage_body),
            (
                "GET",
                "/oss/v2/buckets/bk/objects/obj/signeds3upload",
                signed_upload_body,
            ),
            ("PUT", "/presigned/0", String::new()),
            (
                "POST",
                "/oss/v2/buckets/bk/objects/obj/signeds3upload",
                complete_body,
            ),
            (
                "GET",
                "/data/v1/projects/P/folders/F/contents",
                folder_contents_body,
            ),
            ("POST", "/data/v1/projects/P/items", create_item_body),
        ];
        for (method, prefix, body) in expected {
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut request_line = String::new();
            reader.read_line(&mut request_line).unwrap();
            let mut content_length: usize = 0;
            loop {
                let mut h = String::new();
                if reader.read_line(&mut h).unwrap_or(0) == 0 {
                    break;
                }
                if h == "\r\n" || h == "\n" {
                    break;
                }
                let lower = h.to_ascii_lowercase();
                if let Some(v) = lower.strip_prefix("content-length: ") {
                    content_length = v.trim().parse().unwrap_or(0);
                }
            }
            if content_length > 0 {
                let mut body_bytes = vec![0u8; content_length];
                let _ = reader.read_exact(&mut body_bytes);
                if method == "PUT" {
                    *put_bytes_clone.lock().unwrap() = body_bytes;
                }
            }
            let parts: Vec<&str> = request_line.split_whitespace().collect();
            assert_eq!(parts[0], method, "request_line={request_line:?}");
            assert!(
                parts[1].starts_with(prefix),
                "got {} expected prefix {prefix}",
                parts[1]
            );
            let header = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                body.len()
            );
            let _ = stream.write_all(header.as_bytes());
            let _ = stream.write_all(body.as_bytes());
            let _ = stream.flush();
        }
    });

    let client = make_client(base);
    let uploaded = client
        .upload_file_to_folder("P", "F", &src, None, None)
        .unwrap();
    handle.join().unwrap();
    assert_eq!(uploaded.item_id, "NEW_ITEM");
    assert_eq!(uploaded.version_id, "V1");
    assert_eq!(*put_bytes_received.lock().unwrap(), b"local file contents");
    let _ = EntryType::Items; // keep the import live
}
