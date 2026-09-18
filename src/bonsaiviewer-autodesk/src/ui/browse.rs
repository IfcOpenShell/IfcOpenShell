//! BrowseDialog: hub combo + projects list + lazy-loaded folder tree.
//!
//! UI events (button clicks, selections, expansion) use direct FLTK
//! callbacks that hide/show the window or mutate `Rc<RefCell<State>>` and
//! optionally spawn a worker thread. Worker results come back via one
//! FLTK channel, drained at the top of the event loop. There is no
//! intermediate message bus for plain widget events — clicking Close
//! literally just calls `win.hide()`.

use std::cell::RefCell;
use std::collections::{HashMap, HashSet};
use std::rc::Rc;
use std::sync::Arc;
use std::thread;

use fltk::{
    app,
    browser::HoldBrowser,
    button::Button,
    enums::{Align, Event, Key},
    frame::Frame,
    group::Flex,
    menu::Choice,
    prelude::*,
    tree::{Tree, TreeReason, TreeSelect},
    window::Window,
};

use crate::aps::{ApsClient, Entry, EntryType, Hub, Project};
use crate::auth::AuthSessionService;
use crate::progress::noop_auth;
use crate::rpc::RpcError;
use crate::ui::dialogs::{center_on_screen, drain_after_close, show_error};
use crate::ui::{ensure_app, MODEL_EXTENSIONS};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Ifcfed,
    Model,
    Destination,
}

impl Mode {
    fn title_and_action(self) -> (&'static str, &'static str) {
        match self {
            Mode::Ifcfed => ("Open Project From Autodesk", "Open"),
            Mode::Model => ("Add Model From Autodesk", "Add"),
            Mode::Destination => ("Choose Autodesk Destination", "Select"),
        }
    }
}

#[derive(Clone, Debug)]
pub struct BrowseChoice {
    pub hub: Hub,
    pub project: Project,
    pub entries: Vec<Entry>,
}

const PLACEHOLDER_LABEL: &str = "Loading…";

/// Worker-thread completions. Pure UI events do not go through this — they
/// use direct callbacks. This enum exists only because worker threads
/// cannot touch FLTK widgets.
#[derive(Clone, Debug)]
enum WorkerMsg {
    Hubs(Result<Vec<Hub>, RpcError>),
    Projects(Result<Vec<Project>, RpcError>),
    TopFolders(Result<Vec<Entry>, RpcError>),
    FolderContents(String, Result<Vec<Entry>, RpcError>),
}

struct State {
    hubs: Vec<Hub>,
    selected_hub: Option<usize>,
    projects: Vec<Project>,
    selected_project: Option<usize>,
    tree_entries: HashMap<String, Entry>,
    loaded_folders: HashSet<String>,
    selected_entries: Vec<Entry>,
    result: Option<BrowseChoice>,
}

pub struct BrowseDialog {
    auth: Arc<AuthSessionService>,
    aps: Arc<ApsClient>,
    mode: Mode,
}

impl BrowseDialog {
    pub fn new(auth: Arc<AuthSessionService>, aps: Arc<ApsClient>, mode: Mode) -> Self {
        Self { auth, aps, mode }
    }

    pub fn run(self) -> Result<BrowseChoice, RpcError> {
        ensure_app();
        let (title, action_label) = self.mode.title_and_action();
        let mode = self.mode;
        let multi_select = mode == Mode::Model;

        // ---- Build widgets ----------------------------------------------

        let mut win = Window::default().with_size(920, 620).with_label(title);
        win.make_modal(true);

        let mut root = Flex::default_fill().column();
        root.set_margins(16, 16, 16, 16);
        root.set_spacing(12);

        let mut top = Flex::default().row();
        top.set_spacing(8);
        let mut sign_in = Button::default().with_label("Sign In");
        top.fixed(&sign_in, 100);
        let mut hub_combo = Choice::default();
        hub_combo.add_choice("Select hub");
        hub_combo.set_value(0);
        top.end();
        root.fixed(&top, 32);

        let mut split = Flex::default().row();
        split.set_spacing(8);

        let mut projects_col = Flex::default().column();
        projects_col.set_spacing(4);
        let projects_browser = HoldBrowser::default();
        projects_col.end();
        split.fixed(&projects_col, 280);

        let mut folders_col = Flex::default().column();
        folders_col.set_spacing(4);
        let mut tree = Tree::default();
        tree.set_show_root(false);
        tree.set_root_label("");
        tree.set_select_mode(if multi_select {
            TreeSelect::Multi
        } else {
            TreeSelect::Single
        });
        folders_col.end();

        split.end();

        let status = Frame::default().with_label("Sign in to browse Autodesk projects.");
        let mut status_mut = status.clone();
        status_mut.set_align(Align::Left | Align::Inside);
        root.fixed(&status, 22);

        let mut actions = Flex::default().row();
        actions.set_spacing(8);
        Frame::default();
        let mut cancel_btn = Button::default().with_label("Cancel");
        actions.fixed(&cancel_btn, 100);
        let mut action_btn = Button::default().with_label(action_label);
        action_btn.deactivate();
        actions.fixed(&action_btn, 100);
        actions.end();
        root.fixed(&actions, 32);

        root.end();
        win.end();
        win.make_resizable(true);
        center_on_screen(&mut win);

        // ---- Shared state + worker-result channel -----------------------

        let state: Rc<RefCell<State>> = Rc::new(RefCell::new(State {
            hubs: Vec::new(),
            selected_hub: None,
            projects: Vec::new(),
            selected_project: None,
            tree_entries: HashMap::new(),
            loaded_folders: HashSet::new(),
            selected_entries: Vec::new(),
            result: None,
        }));
        let (worker_tx, worker_rx) = app::channel::<WorkerMsg>();
        let aps = self.aps;
        let auth = self.auth;

        // ---- Direct UI callbacks ----------------------------------------

        cancel_btn.set_callback({
            let mut win = win.clone();
            move |_| win.hide()
        });

        win.handle({
            let mut win = win.clone();
            move |_, ev| match ev {
                Event::KeyDown if app::event_key() == Key::Escape => {
                    win.hide();
                    true
                }
                _ => false,
            }
        });

        sign_in.set_callback({
            let aps = aps.clone();
            let auth = auth.clone();
            let mut status = status_mut.clone();
            move |_| {
                status.set_label("Signing in to Autodesk…");
                let aps = aps.clone();
                let auth = auth.clone();
                thread::spawn(move || {
                    let outcome = auth
                        .login_interactive(noop_auth())
                        .and_then(|_| aps.list_hubs());
                    worker_tx.send(WorkerMsg::Hubs(outcome));
                });
            }
        });

        hub_combo.set_callback({
            let aps = aps.clone();
            let state = state.clone();
            let mut projects_browser = projects_browser.clone();
            let mut tree = tree.clone();
            let mut status = status_mut.clone();
            let action_btn_clone = action_btn.clone();
            move |c| {
                let idx = c.value();
                if idx <= 0 {
                    return;
                }
                let hub_idx = (idx - 1) as usize;
                let mut s = state.borrow_mut();
                if hub_idx >= s.hubs.len() {
                    return;
                }
                s.selected_hub = Some(hub_idx);
                s.selected_project = None;
                s.selected_entries.clear();
                s.projects.clear();
                s.tree_entries.clear();
                s.loaded_folders.clear();
                projects_browser.clear();
                tree.clear();
                tree.redraw();
                refresh_action_button(&mut action_btn_clone.clone(), &s, mode);
                let hub_id = s.hubs[hub_idx].id.clone();
                let hub_name = s.hubs[hub_idx].name.clone();
                drop(s);
                status.set_label(&format!("Loading projects in {hub_name}…"));
                let aps = aps.clone();
                thread::spawn(move || {
                    worker_tx.send(WorkerMsg::Projects(aps.list_projects(&hub_id)));
                });
            }
        });

        projects_browser.clone().set_callback({
            let aps = aps.clone();
            let state = state.clone();
            let mut tree = tree.clone();
            let mut status = status_mut.clone();
            let action_btn_clone = action_btn.clone();
            move |b| {
                let line = b.value();
                if line <= 0 {
                    return;
                }
                let project_idx = (line - 1) as usize;
                let mut s = state.borrow_mut();
                if project_idx >= s.projects.len() {
                    return;
                }
                s.selected_project = Some(project_idx);
                s.selected_entries.clear();
                s.tree_entries.clear();
                s.loaded_folders.clear();
                tree.clear();
                tree.redraw();
                refresh_action_button(&mut action_btn_clone.clone(), &s, mode);
                let hub_id = s
                    .selected_hub
                    .and_then(|i| s.hubs.get(i).map(|h| h.id.clone()))
                    .unwrap_or_default();
                let project_id = s.projects[project_idx].id.clone();
                let project_name = s.projects[project_idx].name.clone();
                drop(s);
                status.set_label(&format!("Loading top folders in {project_name}…"));
                let aps = aps.clone();
                thread::spawn(move || {
                    worker_tx.send(WorkerMsg::TopFolders(
                        aps.list_top_folders(&hub_id, &project_id),
                    ));
                });
            }
        });

        tree.clone().set_callback({
            let aps = aps.clone();
            let state = state.clone();
            let mut status = status_mut.clone();
            let action_btn_clone = action_btn.clone();
            move |t| match t.callback_reason() {
                TreeReason::Selected | TreeReason::Deselected => {
                    let mut s = state.borrow_mut();
                    s.selected_entries = collect_selected_entries(t, &s.tree_entries);
                    update_status_for_selection(&mut status, &s.selected_entries, mode);
                    refresh_action_button(&mut action_btn_clone.clone(), &s, mode);
                }
                TreeReason::Opened => {
                    let Some(item) = t.callback_item() else {
                        return;
                    };
                    let Ok(path) = t.item_pathname(&item) else {
                        return;
                    };
                    let mut s = state.borrow_mut();
                    let Some(entry) = s.tree_entries.get(&path).cloned() else {
                        return;
                    };
                    if entry.entry_type != EntryType::Folders {
                        return;
                    }
                    if s.loaded_folders.contains(&path) {
                        return;
                    }
                    s.loaded_folders.insert(path.clone());
                    // Drop the placeholder so the user doesn't see "Loading…"
                    // alongside the real children once they arrive.
                    if let Some(first_child) = item.child(0) {
                        if first_child.label().as_deref() == Some(PLACEHOLDER_LABEL)
                            && item.child(1).is_none()
                        {
                            let _ = t.remove(&first_child);
                        }
                    }
                    let project_id = s
                        .selected_project
                        .and_then(|i| s.projects.get(i).map(|p| p.id.clone()));
                    drop(s);
                    let Some(project_id) = project_id else { return };
                    let folder_id = entry.id.clone();
                    let aps = aps.clone();
                    thread::spawn(move || {
                        let result =
                            list_folder_contents_for_mode(&aps, &project_id, &folder_id, mode);
                        worker_tx.send(WorkerMsg::FolderContents(path, result));
                    });
                }
                _ => {}
            }
        });

        action_btn.set_callback({
            let state = state.clone();
            let mut win = win.clone();
            move |_| {
                let mut s = state.borrow_mut();
                let valid: Vec<Entry> = s
                    .selected_entries
                    .iter()
                    .filter(|e| is_valid_selection(mode, e))
                    .cloned()
                    .collect();
                if valid.is_empty() {
                    return;
                }
                let (Some(h), Some(p)) = (s.selected_hub, s.selected_project) else {
                    return;
                };
                s.result = Some(BrowseChoice {
                    hub: s.hubs[h].clone(),
                    project: s.projects[p].clone(),
                    entries: valid,
                });
                drop(s);
                win.hide();
            }
        });

        // If we already have a token, populate hubs in the background.
        if auth.get_token().ok().flatten().is_some() {
            let aps = aps.clone();
            thread::spawn(move || {
                worker_tx.send(WorkerMsg::Hubs(aps.list_hubs()));
            });
        }

        // ---- Event loop: pump app, drain worker results ----------------

        win.show();
        while win.shown() {
            app::wait();
            while let Some(msg) = worker_rx.recv() {
                apply_worker_msg(
                    msg,
                    &state,
                    &mut hub_combo,
                    &mut projects_browser.clone(),
                    &mut tree,
                    &mut status_mut,
                    &mut action_btn,
                    mode,
                );
            }
        }
        drain_after_close();

        let result = state.borrow_mut().result.take();
        result.ok_or_else(|| RpcError::internal("User cancelled the Autodesk picker."))
    }
}

// ---- worker-result application -------------------------------------------

#[allow(clippy::too_many_arguments)]
fn apply_worker_msg(
    msg: WorkerMsg,
    state: &Rc<RefCell<State>>,
    hub_combo: &mut Choice,
    projects_browser: &mut HoldBrowser,
    tree: &mut Tree,
    status: &mut Frame,
    action_btn: &mut Button,
    mode: Mode,
) {
    match msg {
        WorkerMsg::Hubs(Err(e)) => show_error("Sign In Failed", &e.message),
        WorkerMsg::Hubs(Ok(hubs)) => {
            let mut s = state.borrow_mut();
            s.hubs = hubs;
            refill_hub_combo(hub_combo, &s.hubs);
            status.set_label("Signed in. Select a hub.");
        }
        WorkerMsg::Projects(Err(e)) => show_error("Load Projects Failed", &e.message),
        WorkerMsg::Projects(Ok(projects)) => {
            let mut s = state.borrow_mut();
            s.projects = projects;
            projects_browser.clear();
            for p in &s.projects {
                projects_browser.add(&p.name);
            }
            if let Some(idx) = s.selected_hub {
                if let Some(hub) = s.hubs.get(idx) {
                    status.set_label(&format!("Hub: {}. Select a project.", hub.name));
                }
            }
        }
        WorkerMsg::TopFolders(Err(e)) => show_error("Load Project Failed", &e.message),
        WorkerMsg::TopFolders(Ok(folders)) => {
            let mut s = state.borrow_mut();
            for entry in folders {
                insert_tree_entry(tree, &mut s.tree_entries, "", &entry);
            }
            tree.redraw();
            if let Some(p) = s.selected_project {
                if let Some(project) = s.projects.get(p) {
                    let line = match mode {
                        Mode::Destination => format!(
                            "Project: {}. Browse folders and choose a destination.",
                            project.name
                        ),
                        _ => format!("Project: {}. Browse folders and pick a file.", project.name),
                    };
                    status.set_label(&line);
                }
            }
        }
        WorkerMsg::FolderContents(parent, Err(e)) => {
            state.borrow_mut().loaded_folders.remove(&parent);
            show_error("Load Folder Failed", &e.message);
        }
        WorkerMsg::FolderContents(parent, Ok(children)) => {
            let mut s = state.borrow_mut();
            for entry in &children {
                insert_tree_entry(tree, &mut s.tree_entries, &parent, entry);
            }
            tree.redraw();
        }
    }
    let _ = action_btn;
}

// ---- worker helpers -------------------------------------------------------

/// Per-mode predicate deciding which listed entries survive.
type EntryFilter = Box<dyn Fn(&Entry) -> bool>;

fn list_folder_contents_for_mode(
    aps: &Arc<ApsClient>,
    project_id: &str,
    folder_id: &str,
    mode: Mode,
) -> Result<Vec<Entry>, RpcError> {
    let object_types: &[&str] = if mode == Mode::Destination {
        &["folders"]
    } else {
        &["folders", "items"]
    };
    let filter_box: Option<EntryFilter> = match mode {
        Mode::Ifcfed => Some(Box::new(|e: &Entry| {
            e.display_name.to_lowercase().ends_with(".ifcfed")
        })),
        Mode::Model => Some(Box::new(|e: &Entry| {
            MODEL_EXTENSIONS
                .iter()
                .any(|ext| e.display_name.to_lowercase().ends_with(ext))
        })),
        Mode::Destination => None,
    };
    let filter_ref: Option<&dyn Fn(&Entry) -> bool> = filter_box.as_deref();
    aps.list_folder_contents(project_id, folder_id, object_types, filter_ref)
}

// ---- widget helpers -------------------------------------------------------

fn refill_hub_combo(combo: &mut Choice, hubs: &[Hub]) {
    combo.clear();
    combo.add_choice("Select hub");
    for hub in hubs {
        combo.add_choice(&hub.name.replace('/', " "));
    }
    combo.set_value(0);
}

fn insert_tree_entry(
    tree: &mut Tree,
    tree_entries: &mut HashMap<String, Entry>,
    parent_canonical: &str,
    entry: &Entry,
) -> String {
    let parent_add = parent_canonical
        .strip_prefix('/')
        .unwrap_or(parent_canonical);
    let label = if entry.display_name.is_empty() {
        entry.id.clone()
    } else {
        entry.display_name.clone()
    };
    let canonical = add_unique(tree, parent_add, &label);
    tree_entries.insert(canonical.clone(), entry.clone());
    if entry.entry_type == EntryType::Folders {
        let inner = canonical.strip_prefix('/').unwrap_or(&canonical);
        let _ = add_unique(tree, inner, PLACEHOLDER_LABEL);
        // FLTK's Fl_Tree_Item defaults to open_=1, which would auto-expand
        // every folder and show the placeholder before the user clicks.
        // Force-collapse so the first user click on the triangle fires the
        // Opened callback we hang lazy-load off.
        if let Some(mut item) = tree.find_item(&canonical) {
            item.close();
        }
    }
    canonical
}

fn add_unique(tree: &mut Tree, parent_add: &str, label: &str) -> String {
    let sanitised = label.replace('/', " ");
    let mut candidate = sanitised.clone();
    let mut counter = 2;
    loop {
        let probe_path = if parent_add.is_empty() {
            candidate.clone()
        } else {
            format!("{parent_add}/{candidate}")
        };
        if tree.find_item(&probe_path).is_none() {
            match tree.add(&probe_path) {
                Some(item) => {
                    return tree
                        .item_pathname(&item)
                        .unwrap_or_else(|_| format!("/{probe_path}"));
                }
                None => return format!("/{probe_path}"),
            }
        }
        candidate = format!("{sanitised} ({counter})");
        counter += 1;
    }
}

fn collect_selected_entries(tree: &Tree, tree_entries: &HashMap<String, Entry>) -> Vec<Entry> {
    let Some(items) = tree.get_selected_items() else {
        return Vec::new();
    };
    items
        .into_iter()
        .filter_map(|item| tree.item_pathname(&item).ok())
        .filter_map(|path| tree_entries.get(&path).cloned())
        .collect()
}

fn update_status_for_selection(status: &mut Frame, entries: &[Entry], mode: Mode) {
    match entries.len() {
        0 => {}
        1 => {
            let entry = &entries[0];
            let kind = match entry.entry_type {
                EntryType::Folders => "folders",
                EntryType::Items => "items",
                EntryType::Other => "entry",
            };
            status.set_label(&format!("Selected {kind}: {}", entry.display_name));
        }
        n => {
            let valid = entries
                .iter()
                .filter(|e| is_valid_selection(mode, e))
                .count();
            status.set_label(&format!("Selected {valid} of {n} items."));
        }
    }
}

fn refresh_action_button(btn: &mut Button, state: &State, mode: Mode) {
    let valid = state
        .selected_entries
        .iter()
        .any(|e| is_valid_selection(mode, e));
    if state.selected_project.is_some() && valid {
        btn.activate();
    } else {
        btn.deactivate();
    }
}

fn is_valid_selection(mode: Mode, entry: &Entry) -> bool {
    match mode {
        Mode::Destination => entry.entry_type == EntryType::Folders,
        Mode::Ifcfed => {
            entry.entry_type == EntryType::Items
                && entry.display_name.to_lowercase().ends_with(".ifcfed")
        }
        Mode::Model => {
            entry.entry_type == EntryType::Items
                && MODEL_EXTENSIONS
                    .iter()
                    .any(|ext| entry.display_name.to_lowercase().ends_with(ext))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn entry(name: &str, ty: EntryType) -> Entry {
        Entry {
            id: name.into(),
            entry_type: ty,
            display_name: name.into(),
            name: None,
            extension_type: String::new(),
        }
    }

    #[test]
    fn is_valid_selection_modes() {
        assert!(is_valid_selection(
            Mode::Ifcfed,
            &entry("a.ifcfed", EntryType::Items)
        ));
        assert!(!is_valid_selection(
            Mode::Ifcfed,
            &entry("a.ifc", EntryType::Items)
        ));
        assert!(is_valid_selection(
            Mode::Model,
            &entry("a.ifc", EntryType::Items)
        ));
        assert!(is_valid_selection(
            Mode::Model,
            &entry("a.rdb", EntryType::Items)
        ));
        assert!(is_valid_selection(
            Mode::Destination,
            &entry("folder", EntryType::Folders)
        ));
        assert!(!is_valid_selection(
            Mode::Destination,
            &entry("file.ifc", EntryType::Items)
        ));
    }
}
