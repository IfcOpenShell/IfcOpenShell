//! Small modal dialogs: filename prompt, confirm, error alert.
//!
//! All three follow the same pattern: build widgets, set each button's
//! callback to mutate a shared `Rc<RefCell<…>>` for the result and call
//! `win.hide()`, then pump `app::wait()` until `win.shown()` is false.

use std::cell::RefCell;
use std::rc::Rc;

use fltk::{
    app,
    button::Button,
    enums::{Align, Event, Key},
    frame::Frame,
    group::Flex,
    input::Input,
    prelude::*,
    window::Window,
};

use crate::ui::ensure_app;

pub fn prompt_for_filename(title: &str, label: &str, default: &str) -> Option<String> {
    ensure_app();

    let mut win = Window::default().with_size(440, 170).with_label(title);
    win.make_modal(true);

    let mut col = Flex::default_fill().column();
    col.set_margins(20, 20, 20, 20);
    col.set_spacing(8);

    let mut lab = Frame::default().with_label(label);
    lab.set_align(Align::Left | Align::Inside);
    col.fixed(&lab, 18);

    let mut entry = Input::default();
    entry.set_value(default);
    let _ = entry.set_position(default.len() as i32);
    col.fixed(&entry, 28);

    Frame::default(); // flexible spacer

    let mut buttons = Flex::default().row();
    buttons.set_spacing(8);
    Frame::default(); // pushes buttons right
    let mut cancel = Button::default().with_label("Cancel");
    buttons.fixed(&cancel, 100);
    let mut ok = Button::default().with_label("OK");
    buttons.fixed(&ok, 100);
    buttons.end();
    col.fixed(&buttons, 32);

    col.end();
    win.end();
    center_on_screen(&mut win);

    let result: Rc<RefCell<Option<String>>> = Rc::new(RefCell::new(None));

    ok.set_callback({
        let entry = entry.clone();
        let mut win = win.clone();
        let result = result.clone();
        move |_| {
            let v = entry.value().trim().to_string();
            if !v.is_empty() {
                *result.borrow_mut() = Some(v);
            }
            win.hide();
        }
    });
    cancel.set_callback({
        let mut win = win.clone();
        move |_| win.hide()
    });
    win.handle({
        let entry = entry.clone();
        let result = result.clone();
        let mut win_for_keys = win.clone();
        move |_, ev| match ev {
            Event::KeyDown => match app::event_key() {
                Key::Enter => {
                    let v = entry.value().trim().to_string();
                    if !v.is_empty() {
                        *result.borrow_mut() = Some(v);
                    }
                    win_for_keys.hide();
                    true
                }
                Key::Escape => {
                    win_for_keys.hide();
                    true
                }
                _ => false,
            },
            _ => false,
        }
    });

    let _ = entry.take_focus();
    win.show();
    while win.shown() {
        app::wait();
    }
    drain_after_close();

    let out = result.borrow_mut().take();
    out
}

pub fn confirm(title: &str, message: &str) -> bool {
    ensure_app();

    let mut win = Window::default().with_size(440, 180).with_label(title);
    win.make_modal(true);

    let mut col = Flex::default_fill().column();
    col.set_margins(20, 20, 20, 20);
    col.set_spacing(8);

    let mut msg = Frame::default().with_label(message);
    msg.set_align(Align::Left | Align::Inside | Align::Wrap);

    let mut buttons = Flex::default().row();
    buttons.set_spacing(8);
    Frame::default();
    let mut no = Button::default().with_label("No");
    buttons.fixed(&no, 100);
    let mut yes = Button::default().with_label("Yes");
    buttons.fixed(&yes, 100);
    buttons.end();
    col.fixed(&buttons, 32);

    col.end();
    win.end();
    center_on_screen(&mut win);

    let answer: Rc<RefCell<bool>> = Rc::new(RefCell::new(false));

    yes.set_callback({
        let mut win = win.clone();
        let answer = answer.clone();
        move |_| {
            *answer.borrow_mut() = true;
            win.hide();
        }
    });
    no.set_callback({
        let mut win = win.clone();
        move |_| win.hide()
    });

    win.show();
    while win.shown() {
        app::wait();
    }
    drain_after_close();

    let out = *answer.borrow();
    out
}

pub fn show_error(title: &str, message: &str) {
    ensure_app();

    let mut win = Window::default().with_size(440, 180).with_label(title);
    win.make_modal(true);

    let mut col = Flex::default_fill().column();
    col.set_margins(20, 20, 20, 20);
    col.set_spacing(8);

    let mut msg = Frame::default().with_label(message);
    msg.set_align(Align::Left | Align::Inside | Align::Wrap);

    let mut buttons = Flex::default().row();
    Frame::default();
    let mut ok = Button::default().with_label("OK");
    buttons.fixed(&ok, 100);
    buttons.end();
    col.fixed(&buttons, 32);

    col.end();
    win.end();
    center_on_screen(&mut win);

    ok.set_callback({
        let mut win = win.clone();
        move |_| win.hide()
    });

    win.show();
    while win.shown() {
        app::wait();
    }
    drain_after_close();
}

pub(crate) fn center_on_screen(win: &mut Window) {
    let (sw, sh) = (app::screen_size().0 as i32, app::screen_size().1 as i32);
    let x = (sw - win.width()) / 2;
    let y = (sh - win.height()) / 2;
    win.set_pos(x.max(0), y.max(0));
}

/// Drain FLTK's pending output after a dialog's event loop exits.
///
/// `Window::hide()` queues an X11 unmap, but FLTK only flushes its X
/// output buffer during an event-loop tick. When a dialog runs inside an
/// RPC handler the connector goes back to a blocking stdin read the
/// moment the dialog returns, so without this helper the window stays
/// visible on screen even though `shown()` is already false. The first
/// few `wait_for(0.0)` calls process any follow-up events the close
/// triggered (focus changes, redraws of newly-exposed windows); the final
/// `flush()` pushes everything out to the X server.
pub(crate) fn drain_after_close() {
    for _ in 0..5 {
        let _ = app::wait_for(0.0);
    }
    app::flush();
}
