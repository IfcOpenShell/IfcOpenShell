# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

# Ensure we don't try to import bpy or blenderbim.bim
# to support running core tests.
# We assume if bpy was never loaded in current python session
# then we're not in Blender. It's still possible to use
# bpy in core and core tests for annotations using TYPE_CHECKING.
IN_BLENDER = sys.modules.get("bpy", None)
if IN_BLENDER:
    import bpy
    import addon_utils

import re
import platform
import traceback
import webbrowser
from collections import deque
from pathlib import Path
from typing import Union, Any


last_commit_hash = "8888888"


def get_last_commit_hash() -> Union[str, None]:
    # Using this weird way to write 8888888,
    # so makefile won't accidentally replace it here
    # we'll be able to distinguish commit hash from placeholder value.
    if last_commit_hash == str(8_888888):
        return None
    return last_commit_hash[:7]


last_error = None
last_actions: deque = deque(maxlen=10)


def get_debug_info():
    version = ".".join(
        [
            str(x)
            for x in [
                addon.bl_info.get("version", (-1, -1, -1))
                for addon in addon_utils.modules()
                if addon.bl_info["name"] == "BlenderBIM"
            ][0]
        ]
    )

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "blender_version": bpy.app.version_string,
        "blenderbim_version": version,
        "blenderbim_commit_hash": get_last_commit_hash(),
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


if IN_BLENDER:
    def get_binary_info() -> dict[str, Any]:
        info = {}
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

        # We can't just use __file__ as blenderbim/__init__.py is typically not symlinked
        # as Blender have errors symlinking main addon package file.
        path = Path(__file__).parent / "bim" / "__init__.py"
        path = path.resolve().parent
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
            import blenderbim.bim

            blenderbim.bim.register()

        def unregister():
            import blenderbim.bim

            blenderbim.bim.unregister()

    except:
        last_error = traceback.format_exc()

        print(last_error)
        print(format_debug_info(get_debug_info()))
        print("\nFATAL ERROR: Unable to load the BlenderBIM Add-on")

        class BIM_PT_fatal_error(bpy.types.Panel):
            bl_label = "BlenderBIM Fatal Error"
            bl_idname = "SCENE_PT_error_message"
            bl_space_type = "PROPERTIES"
            bl_region_type = "WINDOW"
            bl_context = "scene"

            def draw(self, context):
                info = get_debug_info()

                layout = self.layout
                layout.alert = True
                layout.label(text="BlenderBIM could not load.", icon="ERROR")
                if info["os"] == "Windows":
                    layout.operator("wm.console_toggle", text="View the console for full logs.", icon="CONSOLE")
                else:
                    layout.label(text="View the console for full logs.", icon="CONSOLE")
                box = layout.box()
                py = ".".join(info["python_version"].split(".")[0:2])
                b3d = ".".join(info["blender_version"].split(".")[0:2])
                box.label(text="System Information:")
                box.label(text=f"Blender {b3d} {info['os']} {info['machine']}", icon="BLENDER")
                blenderbim_version = info["blenderbim_version"]
                if commit_hash := info.get("blenderbim_commit_hash"):
                    blenderbim_version += f"-{commit_hash}"
                box.label(text=f"Python {py} BBIM {info['blenderbim_version']}", icon="SCRIPTPLUGINS")

                binary_py = get_binary_info().get("binary_python_version")
                if binary_py and py != binary_py:
                    box.separator()
                    box.label(text="BlenderBIM installed for wrong Python version.")
                    box.label(text=f"Expected: {py}. Got: {binary_py}.")
                    box.label(text="Try reinstalling with the correct Python version.")
                    box.label(text="You can download correct version below.")

                layout.operator("bim.copy_debug_information", text="Copy Error Message To Clipboard")
                op = layout.operator("bim.open_uri", text="How Can I Fix This?")
                op.uri = "https://docs.blenderbim.org/users/troubleshooting.html#installation-issues"

                layout.label(text="Try Reinstalling:", icon="IMPORT")
                op = layout.operator("bim.open_uri", text="Re-download Add-on")
                bbim_version = info["blenderbim_version"]
                py_tag = py.replace(".", "")
                if "Linux" in info["os"]:
                    os = "linux"
                elif "Darwin" in info["os"]:
                    if "arm64" in info["machine"]:
                        os = "macosm1"
                    else:
                        os = "macos"
                else:
                    os = "win"
                op.uri = f"https://github.com/IfcOpenShell/IfcOpenShell/releases/download/blenderbim-{bbim_version}/blenderbim-{bbim_version}-py{py_tag}-{os}.zip"

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
