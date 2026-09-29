use std::sync::{Arc, Mutex};

/// Sink for progress reports flowing up to the UI. `(phase, message, percent, detail)`.
pub type Report = Arc<dyn Fn(&str, &str, Option<i32>, Option<&str>) + Send + Sync>;

/// Auth-layer progress (no byte counts): `(phase, message, percent)`.
pub type AuthProgress = Arc<dyn Fn(&str, &str, Option<i32>) + Send + Sync>;

/// APS transfer progress: `(filename, percent, bytes_done, bytes_total)`.
pub type ApsProgress = Arc<dyn Fn(&str, Option<i32>, Option<u64>, Option<u64>) + Send + Sync>;

pub fn noop_auth() -> AuthProgress {
    Arc::new(|_, _, _| {})
}

pub fn noop_report() -> Report {
    Arc::new(|_, _, _, _| {})
}

/// Render a byte count as a short human-readable string (e.g. "3.4 MB").
pub fn format_bytes(value: u64) -> String {
    if value < 1024 {
        return format!("{value} B");
    }
    let mut scaled = value as f64;
    for unit in ["KB", "MB", "GB", "TB"] {
        scaled /= 1024.0;
        if scaled < 1024.0 || unit == "TB" {
            return format!("{scaled:.1} {unit}");
        }
    }
    format!("{value} B")
}

pub fn progress_detail(percent: Option<i32>, done: Option<u64>, total: Option<u64>) -> String {
    let mut parts: Vec<String> = Vec::new();
    if let Some(p) = percent {
        parts.push(format!("{p}%"));
    }
    match (done, total) {
        (Some(d), Some(t)) if t > 0 => {
            parts.push(format!("{} / {}", format_bytes(d), format_bytes(t)))
        }
        (Some(d), _) => parts.push(format_bytes(d)),
        _ => {}
    }
    parts.join(", ")
}

/// Wrap a `Report` sink as a download-side ApsProgress, optionally annotating
/// "(i/N)" when batching. Pass `total = 0` for single-file transfers.
pub fn download_callback(report: Report, index: usize, total: usize) -> ApsProgress {
    Arc::new(move |name, percent, done, total_bytes| {
        let suffix = if total != 0 {
            format!(" ({index}/{total})")
        } else {
            String::new()
        };
        let detail = progress_detail(percent, done, total_bytes);
        let msg = format!("Downloading {name}{suffix}");
        let detail_ref = if detail.is_empty() {
            None
        } else {
            Some(detail.as_str())
        };
        report("download", &msg, percent, detail_ref);
    })
}

pub fn upload_callback(report: Report) -> ApsProgress {
    Arc::new(move |name, percent, done, total_bytes| {
        let detail = progress_detail(percent, done, total_bytes);
        let msg = format!("Uploading {name}");
        let detail_ref = if detail.is_empty() {
            None
        } else {
            Some(detail.as_str())
        };
        report("upload", &msg, percent, detail_ref);
    })
}

/// Adapt an auth-flow sink (no byte counts) onto a `Report` sink.
pub fn auth_to_report(report: Report) -> AuthProgress {
    Arc::new(move |phase, message, percent| {
        report(phase, message, percent, None);
    })
}

/// A single coalesced report: `(phase, message, percent, detail)`.
type PendingReport = (String, String, Option<i32>, Option<String>);

/// Latest-wins hand-off from worker thread → UI thread. Intermediate updates
/// are coalesced: only the freshest matters for a progress bar.
pub struct ProgressBridge {
    pending: Mutex<Option<PendingReport>>,
}

impl ProgressBridge {
    pub fn new() -> Arc<Self> {
        Arc::new(Self {
            pending: Mutex::new(None),
        })
    }

    pub fn report_fn(self: Arc<Self>) -> Report {
        Arc::new(move |phase, message, percent, detail| {
            let mut slot = self.pending.lock().unwrap();
            *slot = Some((
                phase.to_string(),
                message.to_string(),
                percent,
                detail.map(str::to_string),
            ));
        })
    }

    pub fn take(&self) -> Option<(String, String, Option<i32>, Option<String>)> {
        self.pending.lock().unwrap().take()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn format_bytes_units() {
        assert_eq!(format_bytes(0), "0 B");
        assert_eq!(format_bytes(1023), "1023 B");
        assert_eq!(format_bytes(1024), "1.0 KB");
        assert_eq!(format_bytes(1024 * 1024), "1.0 MB");
    }

    #[test]
    fn progress_detail_combines_parts() {
        assert_eq!(
            progress_detail(Some(50), Some(512), Some(1024)),
            "50%, 512 B / 1.0 KB"
        );
        assert_eq!(progress_detail(None, Some(512), None), "512 B");
        assert_eq!(progress_detail(None, None, None), "");
    }

    #[test]
    fn bridge_coalesces_latest() {
        let bridge = ProgressBridge::new();
        let report = bridge.clone().report_fn();
        report("a", "first", None, None);
        report("a", "second", Some(10), Some("d"));
        let taken = bridge.take().unwrap();
        assert_eq!(taken.1, "second");
        assert_eq!(taken.2, Some(10));
        assert!(bridge.take().is_none());
    }
}
