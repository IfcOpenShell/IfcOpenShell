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

import re
import platform
import traceback
import webbrowser
import uuid
import shutil
from collections import deque
from pathlib import Path
from typing import Union, Any, Generator


last_commit_hash = "8888888"


def get_last_commit_hash() -> Union[str, None]:
    # Using this weird way to write 8888888,
    # so makefile won't accidentally replace it here
    # we'll be able to distinguish commit hash from placeholder value.
    if last_commit_hash == str(8_888888):
        return None
    return last_commit_hash[:7]


# Accessed from bonsai extension:
bbim_semver: dict[str, Any] = {}

# Accessed from bonsai dependency:
last_error = None
last_actions: deque = deque(maxlen=20)
FIRST_INSTALLED_BBIM_VERSION: Union[str, None] = None
REINSTALLED_BBIM_VERSION: Union[str, None] = None
REGISTERED_BBIM_PACKAGE: str


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


def get_debug_info():
    bbim_version = bbim_semver["version"]

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "blender_version": bpy.app.version_string,
        "bonsai_version": bbim_version,
        "bonsai_commit_hash": get_last_commit_hash(),
        "last_actions": last_actions,
        "last_error": last_error,
    }


def format_debug_info(info: dict):
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


def safe_link_dlls() -> None:
    # Blender 4.2+ has a problem on Windows for disabling/enabling/reinstalling extensions
    # with loaded binary dependencies (on Windows you can't remove a binary if it's loaded by some program).
    # To avoid this issue we temporary hard link dlls to our temp directory on unregister()
    # (unregister is executed before Blender will try to uninstall dependencies and the issue will arise).
    # Then, Blender won't have a problem unlinking unloaded dlls as they are still linked somewhere.
    # On register() we clean up our temp directory with binaries.
    #
    # TODO: If user uninstalls Bonsai to never use it again, temporary directory won't be cleared.
    #
    # See: https://projects.blender.org/blender/blender/issues/125049
    import bpy

    ext_path = Path(bpy.utils.user_resource("EXTENSIONS"))
    local_path = ext_path / ".local"

    # We use random hash subfolder as user may try to enable/disable addon multiple times.
    random_hash = uuid.uuid4().hex[:8]
    temp_local = ext_path / ".local_temp" / random_hash
    temp_local.mkdir(parents=True)

    for filepath in get_binaries(local_path):
        dest_path = temp_local / filepath.relative_to(local_path)
        dest_path.parent.mkdir(exist_ok=True, parents=True)
        os.link(filepath, dest_path)


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

    try:
        import git

        # We can't just use __file__ as bonsai/__init__.py is typically not symlinked
        # as Blender have errors symlinking main addon package file.
        path = Path(__file__).resolve().parent
        repo = git.Repo(str(path), search_parent_directories=True)
        last_commit_hash = repo.head.object.hexsha
    except:
        pass

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

        def unregister():
            if platform.system() == "Windows":
                safe_link_dlls()

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
                info = get_debug_info()

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
                info = get_debug_info()
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
