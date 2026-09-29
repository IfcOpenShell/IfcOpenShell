use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde::Serialize;
use sha2::{Digest, Sha256};

const APP_DIR: &str = "bonsaiviewer-autodesk";

/// Test seam: when set, overrides the platform cache_root().
static OVERRIDE_ROOT: Mutex<Option<PathBuf>> = Mutex::new(None);

#[cfg(test)]
pub(crate) fn set_root_override(path: Option<PathBuf>) {
    *OVERRIDE_ROOT.lock().unwrap() = path;
}

pub fn cache_root() -> PathBuf {
    if let Some(path) = OVERRIDE_ROOT.lock().unwrap().clone() {
        let _ = fs::create_dir_all(&path);
        return path;
    }
    let root = dirs::cache_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap_or_else(|| PathBuf::from(".")))
        .join(APP_DIR);
    let _ = fs::create_dir_all(&root);
    root
}

fn hash_parts(parts: &[&str]) -> String {
    let mut hasher = Sha256::new();
    for (i, part) in parts.iter().enumerate() {
        if i > 0 {
            hasher.update([0x1f]);
        }
        hasher.update(part.as_bytes());
    }
    let digest = hasher.finalize();
    let mut out = String::with_capacity(64);
    for byte in digest.iter() {
        out.push_str(&format!("{byte:02x}"));
    }
    out
}

/// Stable directory for an .ifcfed; re-downloads overwrite in place so the
/// viewer's open path remains valid across sync operations.
pub fn ifcfed_dir(project_id: &str, item_id: &str) -> PathBuf {
    cache_root()
        .join("ifcfeds")
        .join(hash_parts(&[project_id, item_id]))
}

/// Per-version directory for a model. A new resolved version → a new
/// directory, so sidecars regenerate when the model file changes.
pub fn model_dir(project_id: &str, item_id: &str, version_id: &str) -> PathBuf {
    cache_root()
        .join("models")
        .join(hash_parts(&[project_id, item_id, version_id]))
}

/// Clear the directory so the file we write is the only child.
pub fn prepare_sole_child_dir(dir: &Path) -> std::io::Result<PathBuf> {
    if dir.exists() {
        fs::remove_dir_all(dir)?;
    }
    fs::create_dir_all(dir)?;
    Ok(dir.to_path_buf())
}

fn manifest_path_for(ifcfed: &Path) -> PathBuf {
    let mut name = ifcfed.file_name().unwrap_or_default().to_os_string();
    name.push(".manifest");
    ifcfed.with_file_name(name)
}

pub fn write_manifest<T: Serialize>(ifcfed: &Path, manifest: &T) -> std::io::Result<PathBuf> {
    let path = manifest_path_for(ifcfed);
    let pretty = serde_json::to_string_pretty(manifest)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
    fs::write(&path, pretty + "\n")?;
    Ok(path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    static LOCK: Mutex<()> = Mutex::new(());

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

    #[test]
    fn ifcfed_dir_is_stable_for_same_inputs() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        let a = ifcfed_dir("p1", "i1");
        let b = ifcfed_dir("p1", "i1");
        assert_eq!(a, b);
        let c = ifcfed_dir("p1", "i2");
        assert_ne!(a, c);
    }

    #[test]
    fn model_dir_changes_with_version() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        let v1 = model_dir("p", "i", "v1");
        let v2 = model_dir("p", "i", "v2");
        assert_ne!(v1, v2);
    }

    #[test]
    fn prepare_sole_child_dir_clears_existing() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        let dir = cache_root().join("scratch");
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("stale.txt"), b"old").unwrap();
        prepare_sole_child_dir(&dir).unwrap();
        assert!(dir.read_dir().unwrap().next().is_none());
    }

    #[test]
    fn write_manifest_creates_sidecar() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        let dir = cache_root().join("man");
        fs::create_dir_all(&dir).unwrap();
        let ifcfed = dir.join("model.ifcfed");
        fs::write(&ifcfed, b"data").unwrap();
        let manifest_path = write_manifest(&ifcfed, &json!({"k": "v"})).unwrap();
        assert_eq!(manifest_path.file_name().unwrap(), "model.ifcfed.manifest");
        let read = fs::read_to_string(&manifest_path).unwrap();
        assert!(read.contains("\"k\""));
    }

    #[test]
    fn hash_length_is_full_sha256_hex() {
        let _g = LOCK.lock().unwrap();
        let (_tmp, _guard) = with_tmp();
        let dir = ifcfed_dir("a", "b");
        let basename = dir.file_name().unwrap().to_string_lossy();
        assert_eq!(basename.len(), 64);
    }
}
