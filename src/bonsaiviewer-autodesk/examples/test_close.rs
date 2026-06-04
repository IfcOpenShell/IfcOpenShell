//! Minimal close-button test. Run with:
//!     cargo run --example test_close
//!
//! Expected: a small window opens; clicking "Close" closes it and the
//! program exits with stderr lines tracing what happened. If the window
//! refuses to close, FLTK's hide() is misbehaving on this system and the
//! problem is below the dialog layer.

use fltk::{app, button::Button, prelude::*, window::Window};

fn main() {
    eprintln!("[1] initialising FLTK");
    let app = app::App::default();

    eprintln!("[2] building window");
    let mut win = Window::default()
        .with_size(300, 120)
        .with_label("Close test");
    let mut close_btn = Button::new(100, 40, 100, 40, "Close");
    win.end();
    win.make_modal(true);

    close_btn.set_callback({
        let mut win = win.clone();
        move |_| {
            eprintln!("[5] close button callback fired");
            win.hide();
            eprintln!("[6] after win.hide(), shown() = {}", win.shown());
        }
    });

    eprintln!("[3] win.show()");
    win.show();
    eprintln!("[4] entering app::wait() loop; shown() = {}", win.shown());

    let mut ticks: u32 = 0;
    while win.shown() {
        app.wait();
        ticks += 1;
        if ticks % 100 == 0 {
            eprintln!("    ... still in loop after {ticks} wait() calls, shown() = {}", win.shown());
        }
    }
    eprintln!("[7] loop exited cleanly after {ticks} wait() calls");
}
