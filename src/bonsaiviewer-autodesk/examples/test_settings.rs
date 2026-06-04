//! Open the real SettingsDialog with a no-op on_reload. Run with:
//!     cargo run --release --example test_settings
//!
//! Click "Close" and watch stderr. The settings dialog is the actual code
//! path the host invokes for the `open_settings` RPC — so if Close fails
//! here, it's not a connector-vs-host issue.

use std::sync::Arc;

use bonsaiviewer_autodesk::ui::{ensure_app, SettingsDialog};

fn main() {
    eprintln!("[A] ensure_app()");
    let _ = ensure_app();

    eprintln!("[B] constructing SettingsDialog");
    let dialog = SettingsDialog::new(Arc::new(|| {
        eprintln!("[*] on_reload called");
        Ok(())
    }));

    eprintln!("[C] dialog.run() — click Close (or Save, or Sign Out) now");
    dialog.run();
    eprintln!("[D] dialog.run() returned");
}
