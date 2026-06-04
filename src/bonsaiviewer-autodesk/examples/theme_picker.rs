//! Interactive theme picker. Run with:
//!     cargo run --release --example theme_picker
//!
//! The launcher lists curated theme combinations. Clicking a row starts a
//! separate preview process, applies the chosen theme before any demo
//! widgets are created, and then opens a clean preview window. This avoids
//! stale global FLTK theme state and cached widget colors from previous
//! selections.
//!
//! Once you've found one you like, copy its `apply` call into
//! `src/ui/mod.rs::ensure_app` and rebuild.

use std::cell::Cell;
use std::env;
use std::process::Command;

use fltk::{
    app,
    browser::HoldBrowser,
    button::Button,
    draw,
    enums::{Align, Color, Event, FrameType},
    frame::Frame,
    group::Flex,
    input::Input,
    misc::Progress,
    prelude::*,
    tree::{Tree, TreeSelect},
    window::Window,
};
use fltk_theme::{
    color_themes::{self, fleet},
    ColorMap, ColorTheme, SchemeType, ThemeType, WidgetScheme, WidgetTheme,
};

/// One row in the picker. Any of the three knobs can be `None`.
struct Preset {
    id: &'static str,
    name: &'static str,
    /// FLTK built-in scheme name passed to `app::set_scheme` (e.g. "gtk+",
    /// "gleam", "plastic", "oxy", "base"). `None` keeps whatever the
    /// previous run set.
    fltk_scheme: Option<&'static str>,
    /// fltk-theme `WidgetScheme` overlay (drawing style).
    scheme: Option<SchemeType>,
    /// fltk-theme `WidgetTheme` overlay (default colors).
    theme: Option<ThemeType>,
    /// fltk-theme `ColorTheme` constant (palette).
    color: Option<&'static [ColorMap]>,
}

fn presets() -> Vec<Preset> {
    vec![
        Preset {
            id: "black-aqua",
            name: "Black + Aqua",
            fltk_scheme: None,
            scheme: Some(SchemeType::Aqua),
            theme: None,
            color: Some(color_themes::BLACK_THEME),
        },
        Preset {
            id: "dark-aqua",
            name: "Dark + Aqua",
            fltk_scheme: None,
            scheme: Some(SchemeType::Aqua),
            theme: None,
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "shake-aqua",
            name: "Shake + Aqua",
            fltk_scheme: None,
            scheme: Some(SchemeType::Aqua),
            theme: None,
            color: Some(color_themes::SHAKE_THEME),
        },
        Preset {
            id: "monokai-aqua",
            name: "Monokai + Aqua",
            fltk_scheme: None,
            scheme: Some(SchemeType::Aqua),
            theme: None,
            color: Some(&fleet::MONOKAI),
        },
        Preset {
            id: "material-dark-aqua",
            name: "Material dark + Aqua",
            fltk_scheme: None,
            scheme: Some(SchemeType::Aqua),
            theme: None,
            color: Some(&fleet::MATERIAL_DARK),
        },
        Preset {
            id: "black-sweet",
            name: "Black + Sweet",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: None,
            color: Some(color_themes::BLACK_THEME),
        },
        Preset {
            id: "dark-sweet",
            name: "Dark + Sweet",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: None,
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "shake-sweet",
            name: "Shake + Sweet",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: None,
            color: Some(color_themes::SHAKE_THEME),
        },
        Preset {
            id: "monokai-sweet",
            name: "Monokai + Sweet",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: None,
            color: Some(&fleet::MONOKAI),
        },
        Preset {
            id: "material-dark-sweet",
            name: "Material dark + Sweet",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: None,
            color: Some(&fleet::MATERIAL_DARK),
        },
        Preset {
            id: "widget-theme-dark",
            name: "Widget theme Dark",
            fltk_scheme: None,
            scheme: None,
            theme: Some(ThemeType::Dark),
            color: None,
        },
        Preset {
            id: "gleam-dark",
            name: "Gleam + Dark + dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Gleam),
            theme: Some(ThemeType::Dark),
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "gleam-greybird",
            name: "Gleam + Greybird + gray",
            fltk_scheme: None,
            scheme: Some(SchemeType::Gleam),
            theme: Some(ThemeType::Greybird),
            color: Some(color_themes::GRAY_THEME),
        },
        Preset {
            id: "crystal-dark",
            name: "Crystal + Dark + dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Crystal),
            theme: Some(ThemeType::Dark),
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "fluent-dark",
            name: "Fluent + Dark + dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Fluent),
            theme: Some(ThemeType::Dark),
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "sweet-dark",
            name: "Sweet + Dark + dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Sweet),
            theme: Some(ThemeType::Dark),
            color: Some(color_themes::DARK_THEME),
        },
        Preset {
            id: "fleet1-nord",
            name: "Fleet1 + Nord palette",
            fltk_scheme: None,
            scheme: Some(SchemeType::Fleet1),
            theme: None,
            color: Some(&fleet::NORD),
        },
        Preset {
            id: "fleet2-gruvbox-dark",
            name: "Fleet2 + Gruvbox dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Fleet2),
            theme: None,
            color: Some(&fleet::GRUVBOX_DARK),
        },
        Preset {
            id: "fleet1-monokai",
            name: "Fleet1 + Monokai",
            fltk_scheme: None,
            scheme: Some(SchemeType::Fleet1),
            theme: None,
            color: Some(&fleet::MONOKAI),
        },
        Preset {
            id: "fleet1-solarized-light",
            name: "Fleet1 + Solarized Light",
            fltk_scheme: None,
            scheme: Some(SchemeType::Fleet1),
            theme: None,
            color: Some(&fleet::SOLARIZED_LIGHT),
        },
        Preset {
            id: "clean-greybird",
            name: "Clean + Greybird + gray",
            fltk_scheme: None,
            scheme: Some(SchemeType::Clean),
            theme: Some(ThemeType::Greybird),
            color: Some(color_themes::GRAY_THEME),
        },
        Preset {
            id: "clean-modern-light",
            name: "Clean + modern light",
            fltk_scheme: None,
            scheme: Some(SchemeType::Clean),
            theme: None,
            color: None,
        },
        Preset {
            id: "clean-modern-dark",
            name: "Clean + modern dark",
            fltk_scheme: None,
            scheme: Some(SchemeType::Clean),
            theme: None,
            color: None,
        },
        Preset {
            id: "clean-modern-light-bordered",
            name: "Clean + modern light + borders",
            fltk_scheme: None,
            scheme: Some(SchemeType::Clean),
            theme: None,
            color: None,
        },
        Preset {
            id: "fltk-gtk",
            name: "FLTK gtk+ scheme, no overrides",
            fltk_scheme: Some("gtk+"),
            scheme: None,
            theme: None,
            color: None,
        },
        Preset {
            id: "fltk-plastic",
            name: "FLTK plastic scheme, no overrides",
            fltk_scheme: Some("plastic"),
            scheme: None,
            theme: None,
            color: None,
        },
        Preset {
            id: "fltk-oxy-greybird",
            name: "FLTK oxy scheme + Greybird",
            fltk_scheme: Some("oxy"),
            scheme: None,
            theme: Some(ThemeType::Greybird),
            color: Some(color_themes::GRAY_THEME),
        },
        Preset {
            id: "fltk-oxy-bonsai-dark",
            name: "FLTK oxy scheme + Bonsai dark",
            fltk_scheme: Some("oxy"),
            scheme: None,
            theme: Some(ThemeType::Greybird),
            color: None,
        },
        Preset {
            id: "fltk-oxy-neutral-dark",
            name: "FLTK oxy scheme + neutral dark",
            fltk_scheme: Some("oxy"),
            scheme: None,
            theme: Some(ThemeType::Greybird),
            color: None,
        },
        Preset {
            id: "flat-neutral-dark",
            name: "Flat neutral dark",
            fltk_scheme: Some("base"),
            scheme: None,
            theme: None,
            color: None,
        },
        Preset {
            id: "fltk-default",
            name: "FLTK defaults (no theme)",
            fltk_scheme: None,
            scheme: None,
            theme: None,
            color: None,
        },
    ]
}

fn apply(preset: &Preset) {
    if let Some(s) = preset.fltk_scheme {
        app::set_scheme(match s {
            "gtk+" => app::Scheme::Gtk,
            "plastic" => app::Scheme::Plastic,
            "gleam" => app::Scheme::Gleam,
            "oxy" => app::Scheme::Oxy,
            "base" => app::Scheme::Base,
            _ => app::Scheme::Base,
        });
    }
    if let Some(s) = preset.scheme {
        WidgetScheme::new(s).apply();
    }
    if let Some(t) = preset.theme {
        WidgetTheme::new(t).apply();
    }
    if let Some(c) = preset.color {
        ColorTheme::new(c).apply();
    }
    if preset.id == "fltk-oxy-bonsai-dark" {
        apply_bonsai_dark_palette();
    } else if preset.id == "fltk-oxy-neutral-dark" {
        apply_neutral_dark_palette();
    } else if preset.id == "flat-neutral-dark" {
        apply_flat_neutral_dark_palette();
    } else if preset.id == "clean-modern-light" {
        apply_modern_light_palette();
    } else if preset.id == "clean-modern-dark" {
        apply_modern_dark_palette();
    } else if preset.id == "clean-modern-light-bordered" {
        apply_modern_light_palette();
    }
    eprintln!(
        "[theme] applied: {}  (fltk_scheme={:?}, scheme={:?}, theme={:?}, color={})",
        preset.name,
        preset.fltk_scheme,
        preset.scheme,
        preset.theme,
        preset.color.is_some(),
    );
}

fn apply_bonsai_dark_palette() {
    app::background(38, 41, 47); // #26292f app_background
    app::background2(49, 53, 61); // #31353d control_background
    app::foreground(208, 213, 221); // #d0d5dd primary_text
    app::set_selection_color(83, 199, 99); // #53c763 icon_accent_active_color
    app::set_color(Color::Background, 38, 41, 47);
    app::set_color(Color::BackGround2, 49, 53, 61);
    app::set_color(Color::Foreground, 208, 213, 221);
    app::set_color(Color::Selection, 83, 199, 99);
}

fn apply_neutral_dark_palette() {
    app::background(31, 34, 40);
    app::background2(42, 46, 54);
    app::foreground(222, 226, 232);
    app::set_selection_color(92, 170, 255);
    app::set_color(Color::Background, 31, 34, 40);
    app::set_color(Color::BackGround2, 42, 46, 54);
    app::set_color(Color::Foreground, 222, 226, 232);
    app::set_color(Color::Selection, 92, 170, 255);
}

fn apply_flat_neutral_dark_palette() {
    app::background(24, 26, 31);
    app::background2(34, 37, 44);
    app::foreground(226, 231, 238);
    app::set_selection_color(102, 187, 255);
    app::set_color(Color::Background, 24, 26, 31);
    app::set_color(Color::BackGround2, 34, 37, 44);
    app::set_color(Color::Foreground, 226, 231, 238);
    app::set_color(Color::Selection, 102, 187, 255);
    app::set_frame_type_cb(FrameType::FreeBoxType, draw_flat_box, 6, 3, -10, -6);
}

fn apply_modern_light_palette() {
    app::background(244, 246, 248);
    app::background2(255, 255, 255);
    app::foreground(32, 37, 46);
    app::set_selection_color(34, 132, 245);
    app::set_color(Color::Background, 244, 246, 248);
    app::set_color(Color::BackGround2, 255, 255, 255);
    app::set_color(Color::Foreground, 32, 37, 46);
    app::set_color(Color::Selection, 34, 132, 245);
}

fn apply_modern_dark_palette() {
    app::background(28, 31, 36);
    app::background2(39, 43, 50);
    app::foreground(224, 228, 235);
    app::set_selection_color(82, 164, 255);
    app::set_color(Color::Background, 28, 31, 36);
    app::set_color(Color::BackGround2, 39, 43, 50);
    app::set_color(Color::Foreground, 224, 228, 235);
    app::set_color(Color::Selection, 82, 164, 255);
}

fn find_preset<'a>(presets: &'a [Preset], id: &str) -> Option<&'a Preset> {
    presets.iter().find(|p| p.id == id)
}

/// Brightens a button's fill on Enter, restores on Leave. FLTK widgets are
/// flat by default; this is the tiny per-button helper that gets you a
/// proper hover indication regardless of theme.
fn add_hover(btn: &mut Button) {
    let base = btn.color().lighter();
    btn.set_color(base);
    let stash = Cell::new(btn.color());
    btn.handle(move |b, ev| match ev {
        Event::Enter => {
            stash.set(b.color());
            b.set_color(brighten(b.color(), 24));
            b.redraw();
            true
        }
        Event::Leave => {
            b.set_color(stash.get());
            b.redraw();
            true
        }
        _ => false,
    });
}

fn style_theme_progress(bar: &mut Progress) {
    let fill = bar.selection_color();
    let track = bar.color();
    if fill == track {
        bar.set_selection_color(Color::Selection);
    }
}

fn brighten(c: Color, delta: i32) -> Color {
    let (r, g, b) = c.to_rgb();
    let clamp = |v: i32| v.clamp(0, 255) as u8;
    Color::from_rgb(
        clamp(r as i32 + delta),
        clamp(g as i32 + delta),
        clamp(b as i32 + delta),
    )
}

fn is_flat_neutral_dark(preset: &Preset) -> bool {
    preset.id == "flat-neutral-dark"
}

fn is_clean_modern(preset: &Preset) -> bool {
    matches!(
        preset.id,
        "clean-modern-light" | "clean-modern-dark" | "clean-modern-light-bordered"
    )
}

fn is_clean_modern_dark(preset: &Preset) -> bool {
    preset.id == "clean-modern-dark"
}

fn is_clean_modern_bordered(preset: &Preset) -> bool {
    preset.id == "clean-modern-light-bordered"
}

fn modern_button_color(preset: &Preset) -> Color {
    if is_clean_modern_dark(preset) {
        Color::from_rgb(48, 53, 62)
    } else {
        Color::from_rgb(255, 255, 255)
    }
}

fn modern_button_hover(preset: &Preset) -> Color {
    if is_clean_modern_dark(preset) {
        Color::from_rgb(58, 64, 75)
    } else {
        Color::from_rgb(232, 240, 252)
    }
}

fn modern_button_pressed(preset: &Preset) -> Color {
    if is_clean_modern_dark(preset) {
        Color::from_rgb(35, 39, 46)
    } else {
        Color::from_rgb(218, 229, 246)
    }
}

fn modern_text_color(preset: &Preset) -> Color {
    if is_clean_modern_dark(preset) {
        Color::from_rgb(224, 228, 235)
    } else {
        Color::from_rgb(32, 37, 46)
    }
}

fn modern_accent(preset: &Preset) -> Color {
    if is_clean_modern_dark(preset) {
        Color::from_rgb(82, 164, 255)
    } else {
        Color::from_rgb(34, 132, 245)
    }
}

fn style_modern_button(btn: &mut Button, preset: &Preset) {
    btn.set_frame(if is_clean_modern_bordered(preset) {
        FrameType::BorderBox
    } else {
        FrameType::FlatBox
    });
    btn.set_down_frame(FrameType::FlatBox);
    btn.set_color(modern_button_color(preset));
    btn.set_selection_color(modern_button_pressed(preset));
    btn.set_label_color(modern_text_color(preset));
    let base = modern_button_color(preset);
    let hover = modern_button_hover(preset);
    let pressed = modern_button_pressed(preset);
    btn.handle(move |b, ev| match ev {
        Event::Enter => {
            b.set_color(hover);
            b.redraw();
            true
        }
        Event::Leave => {
            b.set_color(base);
            b.redraw();
            true
        }
        Event::Push => {
            b.set_color(pressed);
            b.redraw();
            false
        }
        Event::Released => {
            b.set_color(hover);
            b.redraw();
            false
        }
        _ => false,
    });
}

fn style_modern_input(input: &mut Input, preset: &Preset) {
    if is_clean_modern_bordered(preset) {
        input.set_frame(FrameType::BorderBox);
    }
    input.set_color(modern_button_color(preset));
    input.set_text_color(modern_text_color(preset));
    input.set_selection_color(modern_accent(preset));
}

fn style_modern_tree(tree: &mut Tree, preset: &Preset) {
    if is_clean_modern_bordered(preset) {
        tree.set_frame(FrameType::BorderBox);
    }
    tree.set_color(modern_button_color(preset));
    tree.set_selection_color(modern_accent(preset));
    tree.set_item_label_fgcolor(modern_text_color(preset));
    tree.set_connector_color(if is_clean_modern_dark(preset) {
        Color::from_rgb(84, 92, 106)
    } else {
        Color::from_rgb(190, 199, 212)
    });
}

fn flat_bg() -> Color {
    Color::from_rgb(24, 26, 31)
}

fn flat_panel() -> Color {
    Color::from_rgb(30, 33, 39)
}

fn flat_control() -> Color {
    Color::from_rgb(34, 37, 44)
}

fn flat_control_hover() -> Color {
    Color::from_rgb(45, 50, 60)
}

fn flat_control_pressed() -> Color {
    Color::from_rgb(26, 29, 35)
}

fn flat_border() -> Color {
    Color::from_rgb(69, 76, 88)
}

fn flat_text() -> Color {
    Color::from_rgb(226, 231, 238)
}

fn flat_accent() -> Color {
    Color::from_rgb(102, 187, 255)
}

fn draw_flat_box(x: i32, y: i32, w: i32, h: i32, color: Color) {
    draw::set_draw_color(color);
    draw::draw_rounded_rectf(x, y, w, h, 3);
    draw::set_draw_color(flat_border());
    draw::draw_rounded_rect(x, y, w, h, 3);
}

fn style_flat_button(btn: &mut Button) {
    btn.set_frame(FrameType::FreeBoxType);
    btn.set_down_frame(FrameType::FreeBoxType);
    btn.set_color(flat_control());
    btn.set_selection_color(flat_control_pressed());
    btn.set_label_color(flat_text());
    btn.handle(move |b, ev| match ev {
        Event::Enter => {
            b.set_color(flat_control_hover());
            b.redraw();
            true
        }
        Event::Leave => {
            b.set_color(flat_control());
            b.redraw();
            true
        }
        Event::Push => {
            b.set_color(flat_control_pressed());
            b.redraw();
            false
        }
        Event::Released => {
            b.set_color(flat_control_hover());
            b.redraw();
            false
        }
        _ => false,
    });
}

fn style_flat_input(input: &mut Input) {
    input.set_frame(FrameType::FreeBoxType);
    input.set_color(flat_control());
    input.set_text_color(flat_text());
    input.set_selection_color(flat_accent());
}

fn style_flat_frame(frame: &mut Frame) {
    frame.set_label_color(flat_text());
}

fn style_flat_tree(tree: &mut Tree) {
    tree.set_frame(FrameType::FreeBoxType);
    tree.set_color(flat_panel());
    tree.set_selection_color(flat_accent());
    tree.set_item_label_fgcolor(flat_text());
    tree.set_item_label_bgcolor(flat_panel());
    tree.set_connector_color(flat_border());
}

fn swatch(label: &str, color: Color) -> Frame {
    let mut frame = Frame::default().with_label(label);
    frame.set_frame(FrameType::FlatBox);
    frame.set_color(color);
    frame.set_label_color(contrast_label(color));
    frame
}

fn contrast_label(color: Color) -> Color {
    let (r, g, b) = color.to_rgb();
    let luminance = (r as u32 * 299 + g as u32 * 587 + b as u32 * 114) / 1000;
    if luminance > 140 {
        Color::Black
    } else {
        Color::White
    }
}

fn connector_progress_colors(preset: &Preset) -> (Color, Color) {
    if preset.id == "fltk-oxy-bonsai-dark" {
        (
            Color::from_rgb(38, 41, 47),  // #26292f app_background
            Color::from_rgb(83, 199, 99), // #53c763 active accent
        )
    } else if preset.id == "fltk-oxy-neutral-dark" {
        (
            Color::from_rgb(31, 34, 40),
            Color::from_rgb(92, 170, 255),
        )
    } else if is_flat_neutral_dark(preset) {
        (flat_bg(), flat_accent())
    } else if is_clean_modern(preset) {
        (
            if is_clean_modern_dark(preset) {
                Color::from_rgb(39, 43, 50)
            } else {
                Color::from_rgb(230, 234, 240)
            },
            modern_accent(preset),
        )
    } else {
        (
            Color::from_rgb(45, 45, 50),
            Color::from_rgb(31, 106, 165),
        )
    }
}

fn run_launcher(presets: Vec<Preset>) {
    let app = app::App::default();

    let mut win = Window::default()
        .with_size(520, 520)
        .with_label("FLTK theme launcher");

    let mut root = Flex::default_fill().column();
    root.set_margins(16, 16, 16, 16);
    root.set_spacing(8);

    let mut header = Frame::default().with_label("Select a preset to open a clean preview process");
    header.set_align(Align::Left | Align::Inside);
    root.fixed(&header, 24);

    let mut list = HoldBrowser::default();
    for p in &presets {
        list.add(p.name);
    }

    root.end();
    win.end();

    list.set_callback(move |b| {
        let line = b.value();
        if line <= 0 {
            return;
        }
        let idx = (line - 1) as usize;
        let Some(preset) = presets.get(idx) else {
            return;
        };
        match env::current_exe() {
            Ok(exe) => {
                if let Err(e) = Command::new(exe).arg("--preview").arg(preset.id).spawn() {
                    eprintln!("[theme] failed to launch preview '{}': {e}", preset.id);
                }
            }
            Err(e) => eprintln!("[theme] could not resolve current executable: {e}"),
        }
    });

    win.show();
    eprintln!("[theme] launcher open - click a preset to launch an isolated preview");
    while win.shown() {
        app.wait();
    }
}

fn run_preview(preset: &Preset) {
    let app = app::App::default();
    apply(preset);

    let mut win = Window::default()
        .with_size(900, 560)
        .with_label(&format!("FLTK theme preview - {}", preset.name));
    if preset.id == "fltk-oxy-bonsai-dark" {
        win.set_color(Color::from_rgb(38, 41, 47));
    } else if preset.id == "fltk-oxy-neutral-dark" {
        win.set_color(Color::from_rgb(31, 34, 40));
    } else if is_flat_neutral_dark(preset) {
        win.set_color(flat_bg());
    } else if is_clean_modern_dark(preset) {
        win.set_color(Color::from_rgb(28, 31, 36));
    } else if is_clean_modern(preset) {
        win.set_color(Color::from_rgb(244, 246, 248));
    }

    let mut root = Flex::default_fill().row();
    root.set_margins(16, 16, 16, 16);
    root.set_spacing(12);

    // ---- Left: selected preset -------------------------------------------
    let mut left = Flex::default().column();
    left.set_spacing(6);
    let mut header = Frame::default().with_label("PRESET");
    header.set_align(Align::Left | Align::Inside);
    if is_flat_neutral_dark(preset) {
        style_flat_frame(&mut header);
    }
    left.fixed(&header, 18);
    let mut selected = Frame::default().with_label(preset.name);
    selected.set_align(Align::Left | Align::Inside | Align::Wrap);
    if is_flat_neutral_dark(preset) {
        style_flat_frame(&mut selected);
    }
    left.fixed(&selected, 60);
    let mut detail = Frame::default().with_label("This preview was launched in a separate process.");
    detail.set_align(Align::Left | Align::Inside | Align::Wrap);
    if is_flat_neutral_dark(preset) {
        style_flat_frame(&mut detail);
    }
    left.fixed(&detail, 48);
    Frame::default();
    left.end();
    root.fixed(&left, 360);

    // ---- Right: demo widgets ---------------------------------------------
    let mut right = Flex::default().column();
    right.set_spacing(8);

    let mut sample_label = Frame::default().with_label("Demo widgets");
    sample_label.set_align(Align::Left | Align::Inside);
    if is_flat_neutral_dark(preset) {
        style_flat_frame(&mut sample_label);
    }
    right.fixed(&sample_label, 22);

    let mut input_row = Flex::default().row();
    input_row.set_spacing(8);
    let mut lab = Frame::default().with_label("Input:");
    lab.set_align(Align::Left | Align::Inside);
    if is_flat_neutral_dark(preset) {
        style_flat_frame(&mut lab);
    }
    input_row.fixed(&lab, 60);
    let mut input = Input::default();
    input.set_value("Some text — try selecting it");
    if is_flat_neutral_dark(preset) {
        style_flat_input(&mut input);
    } else if is_clean_modern(preset) {
        style_modern_input(&mut input, preset);
    }
    input_row.end();
    right.fixed(&input_row, 34);

    let mut button_row = Flex::default().row();
    button_row.set_spacing(8);
    let mut b1 = Button::default().with_label("Primary");
    let mut b2 = Button::default().with_label("Cancel");
    let mut b3 = Button::default().with_label("Sign Out");
    if is_flat_neutral_dark(preset) {
        style_flat_button(&mut b1);
        style_flat_button(&mut b2);
        style_flat_button(&mut b3);
    } else if is_clean_modern(preset) {
        style_modern_button(&mut b1, preset);
        style_modern_button(&mut b2, preset);
        style_modern_button(&mut b3, preset);
    } else {
        add_hover(&mut b1);
        add_hover(&mut b2);
        add_hover(&mut b3);
    }
    button_row.fixed(&b1, 110);
    button_row.fixed(&b2, 110);
    button_row.fixed(&b3, 110);
    Frame::default(); // spacer
    button_row.end();
    right.fixed(&button_row, 34);

    let mut swatch_row = Flex::default().row();
    swatch_row.set_spacing(8);
    let background = swatch("bg", Color::Background);
    let background2 = swatch("bg2", Color::BackGround2);
    let foreground = swatch("fg", Color::Foreground);
    let selection = swatch("sel", Color::Selection);
    swatch_row.fixed(&background, 80);
    swatch_row.fixed(&background2, 80);
    swatch_row.fixed(&foreground, 80);
    swatch_row.fixed(&selection, 80);
    Frame::default();
    swatch_row.end();
    right.fixed(&swatch_row, 34);

    let mut box_row = Flex::default().row();
    box_row.set_spacing(8);
    let mut up = Frame::default().with_label("UpBox");
    up.set_frame(FrameType::UpBox);
    let mut down = Frame::default().with_label("DownBox");
    down.set_frame(FrameType::DownBox);
    let mut thin = Frame::default().with_label("ThinUpBox");
    thin.set_frame(FrameType::ThinUpBox);
    let mut border = Frame::default().with_label("BorderBox");
    border.set_frame(FrameType::BorderBox);
    if is_flat_neutral_dark(preset) {
        for frame in [&mut up, &mut down, &mut thin, &mut border] {
            frame.set_frame(FrameType::FreeBoxType);
            frame.set_color(flat_control());
            frame.set_label_color(flat_text());
        }
    }
    box_row.fixed(&up, 110);
    box_row.fixed(&down, 110);
    box_row.fixed(&thin, 110);
    box_row.fixed(&border, 110);
    Frame::default();
    box_row.end();
    right.fixed(&box_row, 34);

    let mut tree = Tree::default();
    tree.set_show_root(false);
    tree.set_root_label("");
    tree.set_select_mode(TreeSelect::Single);
    if is_flat_neutral_dark(preset) {
        style_flat_tree(&mut tree);
    } else if is_clean_modern(preset) {
        style_modern_tree(&mut tree, preset);
    }
    let _ = tree.add("Project Files/00_General");
    let _ = tree.add("Project Files/01_WIP");
    let _ = tree.add("Project Files/11_IFC/CenterConference.ifc");
    let _ = tree.add("Project Files/11_IFC/Tower.ifc");
    let _ = tree.add("Project Files/04_Archive");
    right.fixed(&tree, 250);

    let mut theme_bar = Progress::default();
    theme_bar.set_minimum(0.0);
    theme_bar.set_maximum(100.0);
    theme_bar.set_value(45.0);
    if is_flat_neutral_dark(preset) {
        theme_bar.set_frame(FrameType::NoBox);
        theme_bar.set_color(flat_bg());
        theme_bar.set_selection_color(flat_accent());
    } else {
        style_theme_progress(&mut theme_bar);
    }
    right.fixed(&theme_bar, 14);

    let mut connector_bar = Progress::default();
    connector_bar.set_minimum(0.0);
    connector_bar.set_maximum(100.0);
    connector_bar.set_value(45.0);
    let (progress_background, progress_fill) = connector_progress_colors(preset);
    if is_flat_neutral_dark(preset) {
        connector_bar.set_frame(FrameType::NoBox);
    }
    connector_bar.set_color(progress_background);
    connector_bar.set_selection_color(progress_fill);
    right.fixed(&connector_bar, 14);

    right.end();
    root.end();
    win.end();

    win.show();
    eprintln!("[theme] preview open: {}", preset.name);
    while win.shown() {
        app.wait();
    }
}

fn main() {
    let presets = presets();
    let args: Vec<String> = env::args().collect();
    if args.get(1).map(String::as_str) == Some("--preview") {
        let Some(id) = args.get(2) else {
            eprintln!("[theme] missing preset id");
            std::process::exit(2);
        };
        let Some(preset) = find_preset(&presets, id) else {
            eprintln!("[theme] unknown preset id: {id}");
            std::process::exit(2);
        };
        run_preview(preset);
    } else {
        run_launcher(presets);
    }
}
