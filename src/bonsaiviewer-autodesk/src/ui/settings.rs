//! Settings dialog: APS client id + OAuth callback port + sign-out.

use std::sync::Arc;

use fltk::{
    app,
    button::Button,
    enums::Align,
    frame::Frame,
    group::Flex,
    input::Input,
    prelude::*,
    window::Window,
};

use crate::auth::{KeyringTokenStore, TokenStore};
use crate::rpc::RpcError;
use crate::settings as cfg;
use crate::ui::dialogs::{center_on_screen, confirm, drain_after_close, show_error};
use crate::ui::ensure_app;

pub struct SettingsDialog {
    pub on_reload: Arc<dyn Fn() -> Result<(), RpcError>>,
}

impl SettingsDialog {
    pub fn new(on_reload: Arc<dyn Fn() -> Result<(), RpcError>>) -> Self {
        Self { on_reload }
    }

    pub fn run(self) {
        ensure_app();
        let client_id = cfg::load_client_id();
        let callback_port = cfg::stored_callback_port();

        let mut win = Window::default()
            .with_size(520, 400)
            .with_label("Autodesk Connector Settings");
        win.make_modal(true);

        let mut col = Flex::default_fill().column();
        col.set_margins(24, 24, 24, 24);
        col.set_spacing(8);

        let mut title = Frame::default().with_label("Autodesk Platform Services");
        title.set_align(Align::Left | Align::Inside);
        col.fixed(&title, 22);

        let mut intro = Frame::default().with_label(
            "The connector signs in to Autodesk using a PKCE flow.\n\
             The client id below comes from your APS application.",
        );
        intro.set_align(Align::Left | Align::Inside | Align::Wrap);
        col.fixed(&intro, 40);

        let mut id_label = Frame::default().with_label("APS client id");
        id_label.set_align(Align::Left | Align::Inside);
        col.fixed(&id_label, 18);

        let id_entry = Input::default();
        let mut id_entry_mut = id_entry.clone();
        id_entry_mut.set_value(&client_id);
        col.fixed(&id_entry, 28);

        let mut port_label = Frame::default().with_label("OAuth callback port");
        port_label.set_align(Align::Left | Align::Inside);
        col.fixed(&port_label, 18);

        let port_entry = Input::default();
        let mut port_entry_mut = port_entry.clone();
        port_entry_mut.set_value(&callback_port.to_string());
        col.fixed(&port_entry, 28);

        let initial_status = if client_id.is_empty() {
            "No client id configured.".to_string()
        } else {
            format!("Signed in as {client_id}")
        };
        let status_label = Frame::default().with_label(&initial_status);
        let mut status_label_mut = status_label.clone();
        status_label_mut.set_align(Align::Left | Align::Inside | Align::Wrap);

        let mut buttons = Flex::default().row();
        buttons.set_spacing(8);
        let mut signout_btn = Button::default().with_label("Sign Out");
        if client_id.is_empty() {
            signout_btn.deactivate();
        }
        buttons.fixed(&signout_btn, 110);
        Frame::default(); // spacer
        let mut close_btn = Button::default().with_label("Close");
        buttons.fixed(&close_btn, 100);
        let mut save_btn = Button::default().with_label("Save");
        buttons.fixed(&save_btn, 100);
        buttons.end();
        col.fixed(&buttons, 32);

        col.end();
        win.end();
        center_on_screen(&mut win);

        // Close: just hide the window. Nothing more.
        close_btn.set_callback({
            let mut win = win.clone();
            move |_| win.hide()
        });

        // Save: validate, persist, reload, hide. Stay open on validation
        // errors so the user can correct without retyping everything.
        save_btn.set_callback({
            let id_entry = id_entry.clone();
            let port_entry = port_entry.clone();
            let mut win = win.clone();
            let on_reload = self.on_reload.clone();
            move |_| {
                let new_id = id_entry.value().trim().to_string();
                let port_str = port_entry.value().trim().to_string();
                let Ok(port_value) = port_str.parse::<u16>() else {
                    show_error(
                        "Invalid Callback Port",
                        "Callback port must be a number between 1 and 65535.",
                    );
                    return;
                };
                if let Err(e) = cfg::save_callback_port(port_value) {
                    show_error("Invalid Callback Port", &e);
                    return;
                }
                cfg::save_client_id(&new_id);
                if let Err(e) = on_reload() {
                    show_error("Reload Failed", &e.message);
                    return;
                }
                win.hide();
            }
        });

        signout_btn.set_callback({
            let mut signout_btn = signout_btn.clone();
            let mut status_label = status_label_mut.clone();
            move |_| {
                let id_now = cfg::load_client_id();
                if id_now.is_empty() {
                    return;
                }
                if !confirm(
                    "Sign Out",
                    &format!("Forget the stored Autodesk session for {id_now}?"),
                ) {
                    return;
                }
                let store = KeyringTokenStore::new(id_now);
                if let Err(e) = store.delete() {
                    show_error("Sign Out Failed", &e.message);
                    return;
                }
                status_label.set_label("Signed out. Next operation will prompt for sign-in.");
                signout_btn.deactivate();
            }
        });

        win.show();
        while win.shown() {
            app::wait();
        }
        drain_after_close();
    }
}
