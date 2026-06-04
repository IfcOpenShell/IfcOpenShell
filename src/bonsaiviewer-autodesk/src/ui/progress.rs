//! ProgressDialog and run_with_progress.
//!
//! `run_with_progress` spawns the caller's work on a background thread and
//! pumps the FLTK event loop on the main thread, draining progress reports
//! through a thread-safe bridge. Returns the worker's result.

use std::sync::{Arc, Mutex};
use std::thread;

use fltk::{app, frame::Frame, group::Flex, misc::Progress, prelude::*, window::Window};

use crate::progress::{ProgressBridge, Report};
use crate::rpc::RpcError;
use crate::ui::dialogs::{center_on_screen, drain_after_close};
use crate::ui::ensure_app;

const WIDTH: i32 = 560;
const HEIGHT: i32 = 160;

pub struct ProgressDialog {
    win: Window,
    title_label: Frame,
    detail_label: Frame,
    bar: Progress,
    determinate: bool,
    /// Animation phase for the indeterminate bar (0..100).
    indeterminate_phase: f64,
}

impl ProgressDialog {
    pub fn new(title: &str) -> Self {
        let _app = ensure_app();
        let mut win = Window::default().with_size(WIDTH, HEIGHT).with_label(title);
        win.make_modal(true);

        let mut col = Flex::default_fill().column();
        col.set_margins(20, 20, 20, 20);
        col.set_spacing(8);

        let mut title_label = Frame::default().with_label(&elide_middle(title, 78));
        title_label.set_align(fltk::enums::Align::Left | fltk::enums::Align::Inside);
        col.fixed(&title_label, 22);

        let mut detail_label = Frame::default().with_label(" ");
        detail_label.set_align(fltk::enums::Align::Left | fltk::enums::Align::Inside);
        col.fixed(&detail_label, 18);

        let mut bar = Progress::default();
        bar.set_minimum(0.0);
        bar.set_maximum(100.0);
        bar.set_value(0.0);
        col.fixed(&bar, 14);

        col.end();
        win.end();
        center_on_screen(&mut win);

        Self {
            win,
            title_label,
            detail_label,
            bar,
            determinate: false,
            indeterminate_phase: 0.0,
        }
    }

    pub fn show(&mut self) {
        self.win.show();
        app::flush();
    }

    pub fn close(&mut self) {
        self.win.hide();
    }

    pub fn visible(&self) -> bool {
        self.win.shown()
    }

    pub fn report(&mut self, message: &str, percent: Option<i32>, detail: Option<&str>) {
        self.title_label.set_label(&elide_middle(message, 78));
        self.detail_label
            .set_label(&elide_middle(detail.unwrap_or(" "), 78));
        match percent {
            Some(p) => {
                self.determinate = true;
                self.bar.set_value(p.clamp(0, 100) as f64);
            }
            None => {
                self.indeterminate_phase = (self.indeterminate_phase + 5.0) % 100.0;
                self.bar.set_value(self.indeterminate_phase);
                self.determinate = false;
            }
        }
        app::flush();
    }
}

/// Show a progress modal and run `work` on a worker thread.
pub fn run_with_progress<T, F>(message: &str, work: F) -> Result<T, RpcError>
where
    F: FnOnce(Report) -> Result<T, RpcError> + Send + 'static,
    T: Send + 'static,
{
    let _app = ensure_app();
    let mut dialog = ProgressDialog::new(message);
    dialog.show();

    let bridge = ProgressBridge::new();
    let report = bridge.clone().report_fn();

    // Shared slot: presence == worker finished. The worker writes here; the
    // UI thread polls each iteration.
    let outcome: Arc<Mutex<Option<Result<T, RpcError>>>> = Arc::new(Mutex::new(None));
    let outcome_for_worker = outcome.clone();
    let handle = thread::spawn(move || {
        *outcome_for_worker.lock().unwrap() = Some(work(report));
    });

    // Pump the event loop until either the worker finishes or the user
    // closes the window. `wait_for(0.03)` keeps the indeterminate bar
    // animating even when there's no UI input.
    while dialog.visible() {
        let _ = app::wait_for(0.03);
        if let Some((_phase, msg, percent, detail)) = bridge.take() {
            dialog.report(&msg, percent, detail.as_deref());
        }
        if outcome.lock().unwrap().is_some() {
            break;
        }
    }

    dialog.close();
    drain_after_close();

    // If the user closed the window before the worker finished, wait it out
    // so we never report success or failure that hasn't actually happened.
    let _ = handle.join();
    let final_outcome = outcome.lock().unwrap().take();
    final_outcome.unwrap_or_else(|| Err(RpcError::internal("Worker thread died unexpectedly.")))
}

fn elide_middle(text: &str, max_chars: usize) -> String {
    let count = text.chars().count();
    if count <= max_chars {
        return text.to_string();
    }
    let head: String = text.chars().take(max_chars / 2).collect();
    let tail: String = text
        .chars()
        .rev()
        .take(max_chars - 1 - max_chars / 2)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect();
    format!("{head}…{tail}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn elide_preserves_short_strings() {
        assert_eq!(elide_middle("hello", 10), "hello");
    }

    #[test]
    fn elide_inserts_ellipsis() {
        let s = elide_middle("abcdefghijklmno", 7);
        assert!(s.contains('…'));
        assert!(s.chars().count() <= 7);
    }
}
