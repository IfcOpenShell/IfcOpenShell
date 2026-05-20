from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Callable, Literal

import customtkinter as ctk

from bonsaiviewer_autodesk import settings
from bonsaiviewer_autodesk.autodesk import ApsClient, AuthSessionService, KeyringTokenStore
from bonsaiviewer_autodesk.rpc import JSONRPC_INTERNAL_ERROR, RpcError

if TYPE_CHECKING:
    from bonsaiviewer_autodesk.connector import AutodeskConnector


MODEL_EXTENSIONS = (".ifc", ".ifcview", ".rdb", ".rdbview")
Mode = Literal["ifcfed", "model", "destination"]


# --- root + Treeview style ---------------------------------------------------
# Tk's default ttk.Treeview looks like Windows 95 in any theme; force-style it
# to match the surrounding CTk dark theme. Every other widget uses CTk defaults.

_root: ctk.CTk | None = None


def ensure_tk_app() -> ctk.CTk:
    global _root
    if _root is None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        _root = ctk.CTk()
        _root.withdraw()
        _apply_treeview_style()
    return _root


def _apply_treeview_style() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Treeview",
        background="#2b2b2b",
        foreground="#dce4ee",
        fieldbackground="#2b2b2b",
        borderwidth=0,
        rowheight=26,
    )
    style.map(
        "Treeview",
        background=[("selected", "#1f6aa5")],
        foreground=[("selected", "#ffffff")],
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])


# --- base modal --------------------------------------------------------------


class _BaseDialog(ctk.CTkToplevel):
    def __init__(self, title: str, *, size: tuple[int, int], resizable: bool = True) -> None:
        super().__init__(ensure_tk_app())
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        if not resizable:
            self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.result: Any = None
        self.withdraw()

    def _on_close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def _center_on_screen(self) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def run(self) -> Any:
        root = ensure_tk_app()
        self._center_on_screen()
        self.deiconify()
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.wait_window()
        try:
            root.update()
            root.update_idletasks()
        except tk.TclError:
            pass
        return self.result


# --- progress ----------------------------------------------------------------


class ProgressDialog(_BaseDialog):
    def __init__(self, title: str = "Working", parent: tk.Misc | None = None) -> None:
        super().__init__(title, size=(440, 130), resizable=False)

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        self.message = ctk.CTkLabel(body, text="Working…", anchor="w")
        self.message.pack(fill="x", anchor="w")

        self.bar = ctk.CTkProgressBar(body, mode="indeterminate")
        self.bar.pack(fill="x", pady=(12, 0))
        self.bar.start()
        self._determinate = False

        self._center_on_screen()
        self.deiconify()
        self.lift()
        self.update()

    def report(self, _phase: str, message: str, percent: int | None = None) -> None:
        try:
            self.message.configure(text=message)
            if percent is None:
                if self._determinate:
                    self.bar.configure(mode="indeterminate")
                    self.bar.start()
                    self._determinate = False
            else:
                if not self._determinate:
                    self.bar.stop()
                    self.bar.configure(mode="determinate")
                    self._determinate = True
                self.bar.set(max(0.0, min(1.0, percent / 100.0)))
            self.update()
        except tk.TclError:
            pass


class _ProgressContext:
    def __init__(self, parent: tk.Misc | None, message: str) -> None:
        self.parent = parent
        self.message = message
        self.dialog: ProgressDialog | None = None

    def __enter__(self) -> Callable[[str, str, int | None], None]:
        self.dialog = ProgressDialog(self.message, self.parent)
        return self.dialog.report

    def __exit__(self, *_exc: object) -> None:
        if self.dialog is not None:
            try:
                self.dialog.withdraw()
                self.dialog.destroy()
            except tk.TclError:
                pass
            self.dialog = None
            try:
                root = ensure_tk_app()
                root.update_idletasks()
                root.update()
            except tk.TclError:
                pass


def progress_dialog(message: str) -> _ProgressContext:
    """Standalone progress dialog usable outside the browse picker."""
    return _ProgressContext(None, message)


# --- browse ------------------------------------------------------------------


class BrowseDialog(_BaseDialog):
    """Hub → project → folder tree → file/folder picker."""

    def __init__(self, *, auth: AuthSessionService, aps: ApsClient, mode: Mode) -> None:
        titles = {
            "ifcfed": ("Open Project From Autodesk", "Open"),
            "model": ("Add Model From Autodesk", "Add"),
            "destination": ("Choose Autodesk Destination", "Select"),
        }
        title, action_label = titles[mode]
        super().__init__(title, size=(920, 620))

        self.auth = auth
        self.aps = aps
        self.mode: Mode = mode
        self.selected_hub: dict[str, Any] | None = None
        self.selected_project: dict[str, Any] | None = None
        self.selected_entry: dict[str, Any] | None = None
        self._tree_entries: dict[str, dict[str, Any]] = {}
        self._project_entries: dict[str, dict[str, Any]] = {}

        self._build_ui(action_label)

    def _build_ui(self, action_label: str) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=16, pady=16)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(root, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(1, weight=1)

        self.sign_in_button = ctk.CTkButton(top, text="Sign In", command=self._sign_in)
        self.sign_in_button.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.hub_combo = ctk.CTkOptionMenu(
            top,
            values=["Select hub"],
            command=self._hub_changed,
            anchor="w",
        )
        self.hub_combo.grid(row=0, column=1, sticky="ew")
        self.hub_combo.configure(state="disabled")

        split = ctk.CTkFrame(root, fg_color="transparent")
        split.grid(row=1, column=0, sticky="nsew")
        split.grid_rowconfigure(0, weight=1)
        split.grid_columnconfigure(0, weight=3, uniform="col")
        split.grid_columnconfigure(1, weight=7, uniform="col")

        self.projects_frame = ctk.CTkFrame(split)
        self.projects_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.tree_frame = ctk.CTkFrame(split)
        self.tree_frame.grid(row=0, column=1, sticky="nsew")

        self.projects = self._make_treeview(self.projects_frame, "PROJECTS")
        self.projects.bind("<<TreeviewSelect>>", lambda _e: self._project_changed())

        self.tree = self._make_treeview(self.tree_frame, "FOLDERS")
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._tree_selection_changed())
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)

        self.status = ctk.CTkLabel(root, text="Sign in to browse Autodesk projects.", anchor="w")
        self.status.grid(row=2, column=0, sticky="ew", pady=(12, 12))

        actions = ctk.CTkFrame(root, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        self.cancel_button = ctk.CTkButton(actions, text="Cancel", command=self._on_close, fg_color="transparent", border_width=1)
        self.cancel_button.grid(row=0, column=1, padx=(0, 8))
        self.action_button = ctk.CTkButton(actions, text=action_label, command=self._confirm)
        self.action_button.grid(row=0, column=2)
        self.action_button.configure(state="disabled")

    def _make_treeview(self, parent: ctk.CTkFrame, header: str) -> ttk.Treeview:
        ctk.CTkLabel(parent, text=header, anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(body, show="tree", selectmode="browse")
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(body, orientation="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    # --- sign-in & population ------------------------------------------------

    def run(self) -> dict[str, Any]:
        if self.auth.get_token() is not None:
            self._populate_hubs_silently()
        outcome = super().run()
        if outcome is None:
            raise RpcError(JSONRPC_INTERNAL_ERROR, "User cancelled the Autodesk picker.")
        return outcome

    def _populate_hubs_silently(self) -> None:
        try:
            hubs = self.aps.list_hubs()
            self._fill_hubs(hubs)
            self.status.configure(text="Signed in. Select a hub.")
        except Exception:
            pass

    def _sign_in(self) -> None:
        with self._with_progress("Signing in to Autodesk") as report:
            try:
                self.auth.login_interactive(report)
                hubs = self.aps.list_hubs()
                self._fill_hubs(hubs)
                self.status.configure(text="Signed in. Select a hub.")
            except Exception as exc:
                show_error(title="Sign In Failed", message=str(exc))

    def _fill_hubs(self, hubs: list[dict[str, Any]]) -> None:
        self._hubs_by_name = {hub["name"]: hub for hub in hubs}
        values = ["Select hub"] + list(self._hubs_by_name.keys())
        self.hub_combo.configure(values=values, state="normal")
        self.hub_combo.set("Select hub")

    def _hub_changed(self, label: str) -> None:
        if label == "Select hub":
            return
        hub = getattr(self, "_hubs_by_name", {}).get(label)
        if not isinstance(hub, dict):
            return
        self.selected_hub = hub
        self.selected_project = None
        self.selected_entry = None
        self._clear_projects()
        self._clear_tree()
        self._refresh_action_button()
        with self._with_progress("Loading Autodesk projects"):
            try:
                projects = self.aps.list_projects(hub["id"])
                self._project_entries = {}
                for project in projects:
                    iid = self.projects.insert("", "end", text=project["name"])
                    self._project_entries[iid] = project
                self.status.configure(text=f"Hub: {hub['name']}. Select a project.")
            except Exception as exc:
                show_error(title="Load Projects Failed", message=str(exc))

    def _project_changed(self) -> None:
        selection = self.projects.selection()
        if not selection or self.selected_hub is None:
            return
        project = self._project_entries.get(selection[0])
        if not isinstance(project, dict):
            return
        self.selected_project = project
        self.selected_entry = None
        self._refresh_action_button()
        self._clear_tree()
        with self._with_progress("Loading top folders"):
            try:
                top_folders = self.aps.list_top_folders(self.selected_hub["id"], project["id"])
                for entry in top_folders:
                    self._insert_tree_entry("", entry)
                if self.mode == "destination":
                    self.status.configure(text=f"Project: {project['name']}. Browse folders and choose a destination.")
                else:
                    self.status.configure(text=f"Project: {project['name']}. Browse folders and pick a file.")
            except Exception as exc:
                show_error(title="Load Project Failed", message=str(exc))

    def _insert_tree_entry(self, parent_iid: str, entry: dict[str, Any]) -> str:
        label = entry.get("display_name") or entry.get("name") or entry.get("id", "?")
        iid = self.tree.insert(parent_iid, "end", text=label)
        self._tree_entries[iid] = entry
        if entry.get("type") == "folders":
            placeholder = self.tree.insert(iid, "end", text="Loading…")
            self._tree_entries[placeholder] = {"__placeholder__": True}
        return iid

    def _on_tree_open(self, _event: tk.Event) -> None:
        selection = self.tree.focus()
        if not selection:
            return
        entry = self._tree_entries.get(selection)
        if not isinstance(entry, dict) or entry.get("type") != "folders" or self.selected_project is None:
            return
        children = self.tree.get_children(selection)
        if len(children) != 1:
            return
        only = self._tree_entries.get(children[0])
        if not (isinstance(only, dict) and only.get("__placeholder__")):
            return

        self.tree.delete(children[0])
        self._tree_entries.pop(children[0], None)

        with self._with_progress("Loading folder contents"):
            try:
                object_types = ["folders"] if self.mode == "destination" else ["folders", "items"]
                contents = self.aps.list_folder_contents(
                    self.selected_project["id"],
                    entry["id"],
                    object_types=object_types,
                    extension_filter=self._extension_filter(),
                )
                for child in contents:
                    self._insert_tree_entry(selection, child)
            except Exception as exc:
                show_error(title="Load Folder Failed", message=str(exc))

    def _extension_filter(self) -> Callable[[dict[str, Any]], bool] | None:
        if self.mode == "ifcfed":
            return lambda entry: (entry.get("display_name") or "").lower().endswith(".ifcfed")
        if self.mode == "model":
            return lambda entry: (entry.get("display_name") or "").lower().endswith(MODEL_EXTENSIONS)
        return None

    def _tree_selection_changed(self) -> None:
        selection = self.tree.selection()
        entry = self._tree_entries.get(selection[0]) if selection else None
        if isinstance(entry, dict) and not entry.get("__placeholder__"):
            self.selected_entry = entry
            name = entry.get("display_name") or entry.get("name") or entry.get("id", "?")
            kind = entry.get("type", "entry")
            self.status.configure(text=f"Selected {kind}: {name}")
        else:
            self.selected_entry = None
        self._refresh_action_button()

    def _refresh_action_button(self) -> None:
        enabled = self.selected_project is not None and self.selected_entry is not None
        if enabled:
            assert self.selected_entry is not None
            if self.mode == "destination":
                enabled = self.selected_entry.get("type") == "folders"
            elif self.mode == "ifcfed":
                enabled = (
                    self.selected_entry.get("type") == "items"
                    and (self.selected_entry.get("display_name") or "").lower().endswith(".ifcfed")
                )
            else:
                enabled = (
                    self.selected_entry.get("type") == "items"
                    and (self.selected_entry.get("display_name") or "").lower().endswith(MODEL_EXTENSIONS)
                )
        self.action_button.configure(state="normal" if enabled else "disabled")

    def _confirm(self) -> None:
        if not self.selected_hub or not self.selected_project or not self.selected_entry:
            return
        self.result = {
            "hub": self.selected_hub,
            "project": self.selected_project,
            "entry": self.selected_entry,
        }
        self._on_close()

    def _clear_projects(self) -> None:
        for iid in self.projects.get_children():
            self.projects.delete(iid)
        self._project_entries.clear()

    def _clear_tree(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._tree_entries.clear()

    def _with_progress(self, message: str) -> _ProgressContext:
        return _ProgressContext(self, message)


# --- filename prompt ---------------------------------------------------------


class _FilenamePrompt(_BaseDialog):
    def __init__(self, *, title: str, label: str, default: str) -> None:
        super().__init__(title, size=(440, 170), resizable=False)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text=label, anchor="w").pack(fill="x")
        self.entry = ctk.CTkEntry(body)
        self.entry.pack(fill="x", pady=(8, 16))
        self.entry.insert(0, default)
        self.entry.select_range(0, "end")
        self.entry.focus_set()

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(buttons, text="Cancel", command=self._on_close, fg_color="transparent", border_width=1).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(buttons, text="OK", command=self._confirm).grid(row=0, column=2)

        self.bind("<Return>", lambda _e: self._confirm())
        self.bind("<Escape>", lambda _e: self._on_close())

    def _confirm(self) -> None:
        value = self.entry.get().strip()
        self.result = value or None
        self._on_close()


def prompt_for_filename(*, title: str, label: str, default: str) -> str | None:
    return _FilenamePrompt(title=title, label=label, default=default).run()


# --- message dialogs (CTk-styled replacements for tkinter.messagebox) --------


class _ConfirmDialog(_BaseDialog):
    def __init__(self, *, title: str, message: str) -> None:
        super().__init__(title, size=(440, 180), resizable=False)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text=message, anchor="w", wraplength=380, justify="left").pack(fill="x", pady=(0, 20))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(buttons, text="No", command=self._on_close, fg_color="transparent", border_width=1).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(buttons, text="Yes", command=self._confirm).grid(row=0, column=2)

        self.bind("<Return>", lambda _e: self._confirm())
        self.bind("<Escape>", lambda _e: self._on_close())

    def _confirm(self) -> None:
        self.result = True
        self._on_close()


class _AlertDialog(_BaseDialog):
    def __init__(self, *, title: str, message: str) -> None:
        super().__init__(title, size=(440, 180), resizable=False)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text=message, anchor="w", wraplength=380, justify="left").pack(fill="x", pady=(0, 20))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(buttons, text="OK", command=self._on_close).grid(row=0, column=1)

        self.bind("<Return>", lambda _e: self._on_close())
        self.bind("<Escape>", lambda _e: self._on_close())


def confirm(*, title: str, message: str) -> bool:
    return bool(_ConfirmDialog(title=title, message=message).run())


def show_error(*, title: str, message: str) -> None:
    _AlertDialog(title=title, message=message).run()


# --- settings ----------------------------------------------------------------


class SettingsDialog(_BaseDialog):
    """Edit the APS client id and sign out."""

    def __init__(self, *, connector: "AutodeskConnector") -> None:
        super().__init__("Autodesk Connector Settings", size=(520, 400), resizable=False)
        self.connector = connector

        env_override = settings.env_client_id()
        stored = settings.stored_client_id()
        effective = env_override or stored
        callback_port = settings.stored_callback_port()

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            body,
            text="Autodesk Platform Services",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            body,
            text="The connector signs in to Autodesk using a PKCE flow. The client id below comes from your APS application.",
            anchor="w",
            wraplength=460,
            justify="left",
        ).pack(fill="x", pady=(2, 16))

        ctk.CTkLabel(body, text="APS client id", anchor="w").pack(fill="x")
        self.client_id_entry = ctk.CTkEntry(body, placeholder_text="Paste your APS client id")
        self.client_id_entry.pack(fill="x", pady=(6, 8))
        self.client_id_entry.insert(0, stored)

        if env_override:
            ctk.CTkLabel(
                body,
                text=f"APS_CLIENT_ID environment variable is set ({env_override}) and overrides the saved value.",
                anchor="w",
                wraplength=460,
                justify="left",
                text_color=("#b45309", "#f59e0b"),
            ).pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(body, text="OAuth callback port", anchor="w").pack(fill="x")
        self.callback_port_entry = ctk.CTkEntry(body, placeholder_text=str(settings.DEFAULT_CALLBACK_PORT))
        self.callback_port_entry.pack(fill="x", pady=(6, 8))
        self.callback_port_entry.insert(0, str(callback_port))

        self.status_label = ctk.CTkLabel(
            body,
            text=f"Signed in as {effective}" if effective else "No client id configured.",
            anchor="w",
            wraplength=460,
            justify="left",
        )
        self.status_label.pack(fill="x", pady=(0, 16))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")
        buttons.grid_columnconfigure(1, weight=1)

        self.signout_button = ctk.CTkButton(
            buttons,
            text="Sign Out",
            command=self._sign_out,
            fg_color="transparent",
            border_width=1,
        )
        self.signout_button.grid(row=0, column=0, sticky="w")
        if not effective:
            self.signout_button.configure(state="disabled")

        ctk.CTkButton(
            buttons,
            text="Close",
            command=self._on_close,
            fg_color="transparent",
            border_width=1,
        ).grid(row=0, column=2, padx=(0, 8))
        ctk.CTkButton(buttons, text="Save", command=self._save).grid(row=0, column=3)

    def _save(self) -> None:
        new_id = self.client_id_entry.get().strip()
        try:
            callback_port = int(self.callback_port_entry.get().strip())
            settings.save_callback_port(callback_port)
        except ValueError:
            show_error(title="Invalid Callback Port", message="Callback port must be a number between 1 and 65535.")
            return
        settings.save_client_id(new_id)
        try:
            self.connector.reload_credentials()
        except Exception as exc:
            show_error(title="Reload Failed", message=str(exc))
            return
        self._on_close()

    def _sign_out(self) -> None:
        client_id = settings.env_client_id() or settings.stored_client_id()
        if not client_id:
            return
        if not confirm(
            title="Sign Out",
            message=f"Forget the stored Autodesk session for {client_id}?",
        ):
            return
        try:
            KeyringTokenStore(service_name="bonsaiviewer-autodesk", username=client_id).delete()
        except RpcError as exc:
            show_error(title="Sign Out Failed", message=exc.message)
            return
        self.status_label.configure(text="Signed out. Next operation will prompt for sign-in.")
        self.signout_button.configure(state="disabled")
