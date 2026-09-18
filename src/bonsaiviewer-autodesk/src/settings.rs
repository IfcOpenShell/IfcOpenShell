use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;

use serde::{Deserialize, Serialize};

pub const DEFAULT_CALLBACK_PORT: u16 = 8080;
const APP_DIR: &str = "bonsaiviewer-autodesk";

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
struct Stored {
    #[serde(default, skip_serializing_if = "String::is_empty")]
    client_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    callback_port: Option<u16>,
}

/// Test seam: when set, overrides the platform config_root().
static OVERRIDE_ROOT: Mutex<Option<PathBuf>> = Mutex::new(None);

#[cfg(test)]
pub(crate) fn set_root_override(path: Option<PathBuf>) {
    *OVERRIDE_ROOT.lock().unwrap() = path;
}

pub fn config_root() -> PathBuf {
    if let Some(path) = OVERRIDE_ROOT.lock().unwrap().clone() {
        let _ = fs::create_dir_all(&path);
        return path;
    }
    let root = dirs::config_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap_or_else(|| PathBuf::from(".")))
        .join(APP_DIR);
    let _ = fs::create_dir_all(&root);
    root
}

fn settings_path() -> PathBuf {
    config_root().join("settings.json")
}

fn read() -> Stored {
    let path = settings_path();
    let Ok(text) = fs::read_to_string(&path) else {
        return Stored::default();
    };
    serde_json::from_str(&text).unwrap_or_default()
}

fn write(data: &Stored) {
    let pretty = serde_json::to_string_pretty(data).unwrap_or_else(|_| "{}".into());
    let _ = fs::write(settings_path(), pretty + "\n");
}

pub fn load_client_id() -> String {
    read().client_id.trim().to_string()
}

pub fn save_client_id(client_id: &str) {
    let mut data = read();
    data.client_id = client_id.trim().to_string();
    write(&data);
}

pub fn stored_callback_port() -> u16 {
    match read().callback_port {
        Some(p) if (1..=u16::MAX).contains(&p) => p,
        _ => DEFAULT_CALLBACK_PORT,
    }
}

pub fn save_callback_port(port: u16) -> Result<(), String> {
    if port == 0 {
        return Err("Callback port must be between 1 and 65535.".into());
    }
    let mut data = read();
    data.callback_port = Some(port);
    write(&data);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    struct RootGuard;
    impl Drop for RootGuard {
        fn drop(&mut self) {
            set_root_override(None);
        }
    }

    fn with_tmp() -> (tempfile::TempDir, RootGuard) {
        let tmp = tempfile::tempdir().unwrap();
        set_root_override(Some(tmp.path().to_path_buf()));
        (tmp, RootGuard)
    }

    // Settings are global; run inside a process-wide lock so parallel tests
    // do not stomp on each other's tmpdir override.
    static LOCK: Mutex<()> = Mutex::new(());

    #[test]
    fn client_id_round_trip() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        assert_eq!(load_client_id(), "");
        save_client_id("  abc123  ");
        assert_eq!(load_client_id(), "abc123");
    }

    #[test]
    fn callback_port_round_trip_and_default() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        assert_eq!(stored_callback_port(), DEFAULT_CALLBACK_PORT);
        save_callback_port(9090).unwrap();
        assert_eq!(stored_callback_port(), 9090);
    }

    #[test]
    fn corrupt_settings_yields_defaults() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        fs::write(settings_path(), "{not json").unwrap();
        assert_eq!(load_client_id(), "");
        assert_eq!(stored_callback_port(), DEFAULT_CALLBACK_PORT);
    }

    #[test]
    fn rejects_port_zero() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        assert!(save_callback_port(0).is_err());
    }
}
