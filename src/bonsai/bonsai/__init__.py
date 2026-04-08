# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

# Ensure we don't try to import bpy or bonsai.bim
# to support running core tests.
# We assume if bpy was never loaded in current python session
# then we're not in Blender. It's still possible to use
# bpy in core and core tests for annotations using TYPE_CHECKING.
IN_BLENDER = sys.modules.get("bpy", None)
if IN_BLENDER:
    import bpy

# This file is executed twice - first as a bonsai-extension
# and then as a bonsai-package.
IN_PACKAGE = __package__ == "bonsai"

import platform
import re
import traceback
import webbrowser
from collections import deque
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

last_commit_hash = "8888888"
last_commit_date = "9999999"
last_git_branch = "7777777"


def get_last_commit_hash() -> Union[str, None]:
    # Using this weird way to write 8888888,
    # so makefile won't accidentally replace it here
    # we'll be able to distinguish commit hash from placeholder value.
    if last_commit_hash == str(8_888888):
        return None
    return last_commit_hash[:7]


def get_last_commit_date() -> Union[str, None]:
    if last_commit_date == str(9_999999):
        return None
    return last_commit_date


def get_git_branch() -> Union[str, None]:
    # Using this weird way to write 7777777,
    # so makefile won't accidentally replace it here
    # we'll be able to distinguish branch from placeholder value.
    if last_git_branch == str(7_777777):
        return None
    return last_git_branch


# Accessed from bonsai extension:
bbim_semver: dict[str, Any] = {}

# Accessed from bonsai dependency:
last_error = None
last_actions: deque = deque(maxlen=20)
FIRST_INSTALLED_BBIM_VERSION: Union[str, None] = None
REINSTALLED_BBIM_VERSION: Union[str, None] = None
REGISTERED_BBIM_PACKAGE: str


def is_registering() -> bool:
    """
    During addon registration ``bpy.context`` and ``bpy.data`` are restricted
    and you can't access their properties.
    """
    import bpy

    if TYPE_CHECKING or bpy.app.version >= (5, 0, 0):
        import _bpy_restrict_state as bpy_restrict_state
    else:
        import bpy_restrict_state

    return isinstance(bpy.context, bpy_restrict_state._RestrictContext)


def initialize_bbim_semver():
    """Initialize `bbim_semver` dictionary.

    Blender doesn't seem to store a full extension version (only major-minor-patch)
    in `addon_utils.modules()->bl_info['version']`,
    therefore we just parse it from .toml.
    """
    import tomllib

    toml_path = Path(__file__).parent / "blender_manifest.toml"
    with open(toml_path, "rb") as f:
        manifest = tomllib.load(f)
    semver_pattern = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    version_str = manifest["version"]
    re_version = re.match(semver_pattern, version_str)
    assert re_version
    global bbim_semver
    bbim_semver = re_version.groupdict()
    bbim_semver["version"] = version_str


def get_debug_info(*, bonsai_failed_to_load: bool = False) -> dict[str, Any]:
    import bpy

    bbim_version = bbim_semver["version"]

    # All data here should be gettable even in case of `bpy.context` and `bpy.data` being inaccessible
    # and Bonsai completely failed to load.
    debug_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "blender_version": bpy.app.version_string,
        "bonsai_version": bbim_version,
        "bonsai_commit_hash": get_last_commit_hash(),
        "bonsai_commit_date": get_last_commit_date(),
        "bonsai_git_branch": get_git_branch(),
        "last_actions": last_actions,
        "last_error": last_error,
    }

    # Can't access blend data or context during registration.
    # If Bonsai failed to load we cannot safely access any of its properties or its tools
    # as they may not be registered yet and acessing them will break Bonsai Fatal Error UI.
    if is_registering() or bonsai_failed_to_load:
        return debug_info

    import bonsai.tool as tool

    # Add .blend file save information
    if bpy.data.is_saved:
        debug_info["blend_file_path"] = bpy.data.filepath
        debug_info["blend_file_dirty"] = bpy.data.is_dirty
    else:
        debug_info["blend_file_path"] = "Not saved"
        debug_info["blend_file_dirty"] = "N/A"

    # Add IFC file information
    bim_props = tool.Blender.get_bim_props()
    if bim_props.ifc_file:
        debug_info["ifc_file_path"] = bim_props.ifc_file
        debug_info["ifc_is_dirty"] = bim_props.is_dirty
    else:
        debug_info["ifc_file_path"] = "No IFC loaded"
        debug_info["ifc_is_dirty"] = "N/A"

    return debug_info


def format_debug_info(info: dict[str, Any]) -> str:
    last_actions = ""
    for action in info["last_actions"]:
        last_actions += f"\n# {action['type']}: {action['name']}"
        if settings := action.get("settings"):
            last_actions += f"\n>>> {settings}"
    info["last_actions"] = last_actions
    text = "\n".join(f"{k}: {v}" for k, v in info.items())
    return text.strip()


def get_binaries(path: Path) -> Generator[Path, None, None]:
    yield from path.glob("**/*.pyd")
    yield from path.glob("**/*.dll")
    # pyradiance is using .so files on windows for some reason.
    yield from path.glob("**/*.so")


# TODO: remove before 0.8.6 release.
# On Windows issues with removing extensions were resolved in Blender 4.3,
# but we removed our workaround that was producing some junk only in 0.8.5 release.
# So we're temporarily keeping the part that's cleaning up outputs from previous releases.
def clean_up_dlls_safe_links() -> None:
    import bpy

    ext_path = Path(bpy.utils.user_resource("EXTENSIONS"))
    temp_path = ext_path / ".local_temp"
    if not temp_path.exists():
        return

    for filepath in get_binaries(temp_path):
        try:
            os.unlink(filepath)
        except PermissionError:
            pass

    def is_empty_directory(directory: Path) -> bool:
        return not any(directory.iterdir())

    def remove_empty_folders(folder: Path) -> None:
        for subfolder in folder.iterdir():
            if subfolder.is_dir():
                remove_empty_folders(subfolder)

        if is_empty_directory(folder):
            folder.rmdir()

    remove_empty_folders(temp_path)


if IN_BLENDER:
    import bpy

    initialize_bbim_semver()

    def get_binary_info() -> dict[str, Any]:
        info = {}
        py_version = sys.version_info
        site_path = (
            Path(bpy.utils.user_resource("EXTENSIONS"))
            / ".local"
            / "lib"
            / f"python{py_version.major}.{py_version.minor}"
            / "site-packages"
        )
        lib = site_path / "ifcopenshell"
        binary = next((i for i in lib.glob("_ifcopenshell_wrapper.*")), None)
        if binary is None:
            info["binary_error"] = "Couldn't find ifcopenshell wrapper binary."
            return info

        # Examples:
        # _ifcopenshell_wrapper.cp311-win_amd64.pyd
        # _ifcopenshell_wrapper.cpython-311-darwin.so
        # _ifcopenshell_wrapper.cpython-311-x86_64-linux-gnu.so
        binary = binary.name
        info["binary_file_name"] = binary
        pattern = re.compile(r"cp(\d+)|cpython-(\d+)")
        match = pattern.search(binary)
        if not match:
            info["binary_error"] = f"Couldn't parse binary version from '{binary}'."
            return info

        version = match.group(1) or match.group(2)
        version = f"{version[0]}.{version[1:]}"
        info["binary_python_version"] = version
        return info

    def update_commit_data() -> None:
        try:
            import git

            global last_commit_hash
            global last_commit_date
            global last_git_branch
            path = Path(__file__).resolve().parent
            repo = git.Repo(str(path), search_parent_directories=True)
            last_commit_hash = repo.head.object.hexsha
            last_commit_date = repo.head.object.committed_datetime.isoformat()
            last_git_branch = repo.active_branch.name
        except:
            pass

    if IN_PACKAGE:
        update_commit_data()

    try:
        import ifcopenshell.api

        def log_api(usecase_path, ifc_file, settings):
            last_actions.append(
                {
                    "type": "ifcopenshell.api",
                    "name": usecase_path,
                    "settings": ifcopenshell.api.serialise_settings(settings),
                }
            )

        ifcopenshell.api.add_pre_listener("*", "action_logger", log_api)

        def purge_cache():
            """Purge cache left from previous session (e.g. after reload or update)."""
            import bonsai.tool as tool

            tool.Blender.get_bonsai_version.cache_clear()

        def register():
            if platform.system() == "Windows":
                clean_up_dlls_safe_links()

            import bonsai

            bonsai.REGISTERED_BBIM_PACKAGE = __package__

            import bonsai.bim

            current_version = bbim_semver["version"]
            if bonsai.FIRST_INSTALLED_BBIM_VERSION is None:
                bonsai.FIRST_INSTALLED_BBIM_VERSION = current_version
            elif not bonsai.REINSTALLED_BBIM_VERSION and bonsai.FIRST_INSTALLED_BBIM_VERSION != current_version:
                bonsai.REINSTALLED_BBIM_VERSION = current_version

            bonsai.bim.register()
            purge_cache()

        def unregister():
            import bonsai.bim

            bonsai.bim.unregister()

    except:

        def show_scene_properties() -> None:
            # By default in Blender object properties are selected.
            # Or user may have some other properties selected in their startup file.
            # Select scene properties to ensure user will see our error handler.
            for area in bpy.context.screen.areas:
                if area.type != "PROPERTIES":
                    continue
                space = area.spaces.active
                assert isinstance(space, bpy.types.SpaceProperties)
                space.context = "SCENE"

        # Use a timer as we're not allowed to make changes to data during register().
        bpy.app.timers.register(show_scene_properties, first_interval=0.1)

        last_error = traceback.format_exc()

        print(last_error)
        print(format_debug_info(get_debug_info()))
        print("\nFATAL ERROR: Unable to load Bonsai")

        class BIM_PT_fatal_error(bpy.types.Panel):
            bl_label = "Bonsai Fatal Error"
            bl_idname = "SCENE_PT_error_message"
            bl_space_type = "PROPERTIES"
            bl_region_type = "WINDOW"
            bl_context = "scene"

            def draw(self, context):
                info = get_debug_info(bonsai_failed_to_load=True)

                layout = self.layout
                layout.alert = True
                layout.label(text="Bonsai could not load.", icon="ERROR")
                if info["os"] == "Windows":
                    layout.operator("wm.console_toggle", text="View the console for full logs.", icon="CONSOLE")
                else:
                    layout.label(text="View the console for full logs.", icon="CONSOLE")
                box = layout.box()
                py = ".".join(info["python_version"].split(".")[0:2])
                b3d = ".".join(info["blender_version"].split(".")[0:2])
                box.label(text="System Information:")
                box.label(text=f"Blender {b3d} {info['os']} {info['machine']}", icon="BLENDER")
                bonsai_version = info["bonsai_version"]
                if commit_hash := info.get("bonsai_commit_hash"):
                    bonsai_version += f"-{commit_hash}"
                box.label(text=f"Python {py} BBIM {info['bonsai_version']}", icon="SCRIPTPLUGINS")

                binary_py = get_binary_info().get("binary_python_version")
                if binary_py and py != binary_py:
                    box.separator()
                    # From wrong-platform-build issues we're guarded by Blender extension installation.
                    # But Blender currently doesn't support separate builds for different Python version,
                    # so those issues might still slip in.
                    box.label(text="Bonsai installed for wrong Python version.")
                    box.label(text=f"Expected binary version: {py}. Got: {binary_py}.")
                    # On reinstallation, dependencies versions doesn't change, so Blender will just ignore new dependencies.
                    # So, we need to make user will disable an extension (just uninstallation won't remove dependencies).
                    # Blender restart doesn't seem to be required in that case
                    # as dependencies failed to load due to Python version mismatch.
                    box.label(text="Try reinstalling with the correct Python version.")
                    box.label(text="Before reinstallation make sure to")
                    box.label(text="DISABLE Bonsai (uninstallation won't help).")
                    if py == "3.11":
                        box.label(text="You can download correct version below.")
                    else:
                        box.label(text="Since you're using Python >3.11,")
                        box.label(text="installation from Blender extensions platform")
                        box.label(text="is not supported and you need to download")
                        box.label(text="and install Bonsai from the link below.")

                layout.operator("bim.copy_debug_information", text="Copy Error Message To Clipboard")
                op = layout.operator("bim.open_uri", text="How Can I Fix This?")
                op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html#installation-issues"

                layout.label(text="Try Reinstalling:", icon="IMPORT")
                op = layout.operator("bim.open_uri", text="Re-download Add-on")
                bbim_version = info["bonsai_version"]
                py_tag = py.replace(".", "")
                if "Linux" in info["os"]:
                    os = "linux-x64"
                elif "Darwin" in info["os"]:
                    if "arm64" in info["machine"]:
                        os = "macos-arm64"
                    else:
                        os = "macos-x64"
                else:
                    os = "windows-x64"
                op.uri = f"https://github.com/IfcOpenShell/IfcOpenShell/releases/download/bonsai-{bbim_version}/bonsai_py{py_tag}-{bbim_version}-{os}.zip"

        class OpenUri(bpy.types.Operator):
            bl_idname = "bim.open_uri"
            bl_label = "Open URI"
            uri: bpy.props.StringProperty()

            def execute(self, context):
                webbrowser.open(self.uri)
                return {"FINISHED"}

        class CopyDebugInformation(bpy.types.Operator):
            bl_idname = "bim.copy_debug_information"
            bl_label = "Copy Debug Information"
            bl_description = "Copies debugging information to your clipboard for use in bugreports"

            def execute(self, context):
                info = get_debug_info(bonsai_failed_to_load=True)
                info.update(get_binary_info())
                info = format_debug_info(info)
                context.window_manager.clipboard = info
                return {"FINISHED"}

        class HiddenPanel:
            @classmethod
            def false_poll(cls, context):
                return False

        def register():
            # Only show our error panel and nothing else in the scene tab
            for item_name in dir(bpy.types):
                item = getattr(bpy.types, item_name)
                if not hasattr(item, "bl_rna") or not isinstance(item.bl_rna, bpy.types.Panel):
                    continue
                if getattr(item, "bl_context", None) != "scene":
                    continue

                # Reregister scene panel with a new poll to hide it
                item.poll = HiddenPanel.false_poll
                bpy.utils.unregister_class(item)
                bpy.utils.register_class(item)
            bpy.utils.register_class(BIM_PT_fatal_error)
            bpy.utils.register_class(CopyDebugInformation)
            bpy.utils.register_class(OpenUri)

        def unregister():
            bpy.utils.unregister_class(OpenUri)
            bpy.utils.unregister_class(CopyDebugInformation)
            bpy.utils.unregister_class(BIM_PT_fatal_error)
