//! FLTK-based dialogs.
//!
//! Each dialog opens its own modal `Window` and pumps the shared FLTK event
//! loop until the window closes. Unlike eframe::run_simple_native, FLTK
//! creates the app object exactly once (via [`ensure_app`]) and every
//! dialog reuses it — opening and closing windows in sequence is the
//! intended pattern, not an edge case.

pub mod browse;
pub mod dialogs;
pub mod progress;
pub mod settings;

use std::sync::OnceLock;

use fltk::app;
use fltk_theme::{color_themes::fleet, ColorTheme, SchemeType, WidgetScheme};

pub use browse::{BrowseDialog, Mode};
pub use dialogs::prompt_for_filename;
pub use progress::run_with_progress;
pub use settings::SettingsDialog;

pub const MODEL_EXTENSIONS: &[&str] = &[".ifc", ".ifcview", ".rdb", ".rdbview"];

static APP_INIT: OnceLock<app::App> = OnceLock::new();

/// Initialise FLTK exactly once. Subsequent calls return the same handle.
pub fn ensure_app() -> app::App {
    *APP_INIT.get_or_init(|| {
        let a = app::App::default();
        WidgetScheme::new(SchemeType::Aqua).apply();
        ColorTheme::new(&fleet::MATERIAL_DARK).apply();
        app::set_font_size(13);
        app::set_visible_focus(false);
        a
    })
}
