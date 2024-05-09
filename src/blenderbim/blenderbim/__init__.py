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
import bpy
import platform
import traceback
import subprocess
import webbrowser
import addon_utils
from collections import deque

bl_info = {
    "name": "BlenderBIM",
    "description": "Transforms Blender into a native Building Information Model authoring platform using IFC.",
    "author": "IfcOpenShell Contributors",
    "blender": (3, 1, 0),
    "version": (0, 0, 999999),
    "location": "File Menu, Scene Properties Tab. See documentation for more.",
    "doc_url": "https://docs.blenderbim.org/",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "System",
}

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


if sys.modules.get("bpy", None):
    # Process *.pth in /libs/site/packages to setup globally importable modules
    # This is 3 levels deep as required by the static RPATH of ../../ from dependencies taken from Anaconda
    # site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))

    try:
        import blenderbim.bim
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
            blenderbim.bim.register()

        def unregister():
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
                layout = self.layout
                layout.label(text="BlenderBIM could not load.", icon="ERROR")
                layout.label(text="View the console for full logs.", icon="CONSOLE")
                box = layout.box()
                info = get_debug_info()
                py = ".".join(info["python_version"].split(".")[0:2])
                b3d = ".".join(info["blender_version"].split(".")[0:2])
                box.label(text=f"Blender {b3d} {info['os']} {info['machine']}", icon="BLENDER")
                box.label(text=f"Python {py} BBIM {info['blenderbim_version']}", icon="SCRIPTPLUGINS")
                layout.operator("bim.copy_debug_information", text="Copy Error Message To Clipboard")
                op = layout.operator("bim.open_uri", text="How Can I Fix This?")
                op.uri = "https://docs.blenderbim.org/users/troubleshooting.html#installation-issues"

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
                info = format_debug_info(get_debug_info())

                if platform.system() == "Windows":
                    command = "echo | set /p nul=" + info
                elif platform.system() == "Darwin":  # for MacOS
                    command = 'printf "' + info.replace("\n", "\\n").replace('"', "") + '" | pbcopy'
                else:  # Linux
                    command = 'printf "' + info.replace("\n", "\\n").replace('"', "") + '" | xclip -selection clipboard'
                subprocess.run(command, shell=True, check=True)
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
