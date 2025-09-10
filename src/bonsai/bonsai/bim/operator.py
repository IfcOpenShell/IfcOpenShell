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
import contextlib
import bpy
import bmesh
import time
import logging
import textwrap
import shutil
import platform
import subprocess
import tempfile
import webbrowser
import ifcopenshell
import bonsai.bim
import bonsai.tool as tool
import bonsai.bim.handler
from enum import Enum
from bpy_extras.io_utils import ImportHelper
from bonsai.bim import import_ifc
from bonsai.bim.prop import StrProperty
from bonsai.bim.ui import IFCFileSelector
from bonsai.bim.helper import get_enum_items
from mathutils import Vector, Euler
from math import radians
from pathlib import Path
from collections import namedtuple
from typing import Union, TYPE_CHECKING, Literal, get_args
from collections.abc import Iterable
from natsort import natsorted

if TYPE_CHECKING:
    from bonsai.bim.prop import MultipleFileSelect, Attribute
    from bpy.stub_internal import rna_enums


class SetTab(bpy.types.Operator):
    bl_idname = "bim.set_tab"
    # NOTE: bl_label is set to empty string intentionally
    # to avoid showing the operator's name in the tooltips, see #3704
    bl_label = ""
    bl_options = {"INTERNAL"}
    tab: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return next((t[1] for t in bonsai.bim.prop.get_tab(None, context) if t[0] == operator.tab), "")

    def execute(self, context):
        if context.area.spaces.active.search_filter:
            return {"FINISHED"}
        tool.Blender.setup_tabs()
        aprops = tool.Blender.get_area_props(context)
        aprops.tab = self.tab
        return {"FINISHED"}


class SwitchTab(bpy.types.Operator):
    bl_idname = "bim.switch_tab"
    bl_label = "Switch Tab"
    bl_options = set()
    bl_description = "Switches to the last used tab"

    def execute(self, context):
        if context.area.spaces.active.search_filter:
            return {"FINISHED"}
        tool.Blender.setup_tabs()
        aprops = tool.Blender.get_area_props(context)
        aprops.tab = aprops.alt_tab
        return {"FINISHED"}


class OpenUri(bpy.types.Operator):
    bl_idname = "bim.open_uri"
    bl_label = "Open URI"
    uri: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return f"Open the URL in your Web Browser: '{properties.uri}'."

    def execute(self, context):
        webbrowser.open(self.uri)
        return {"FINISHED"}


class OpenPath(bpy.types.Operator):
    bl_idname = "bim.open_path"
    bl_label = "Open Path"
    path: bpy.props.StringProperty()
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.tooltip:
            return properties.tooltip
        return f"Open path: '{properties.path}'."

    def execute(self, context):
        tool.Blender.open_file_or_folder(self.path)
        return {"FINISHED"}


class CloseError(bpy.types.Operator):
    bl_idname = "bim.close_error"
    bl_label = "Close Error"

    def execute(self, context):
        bonsai.last_error = None
        return {"FINISHED"}

    def draw(self, context):
        col = self.layout.column()
        col.label(text="Warning: your model may be damaged.")
        col.label(text="Really continue?")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CloseBlendWarning(bpy.types.Operator):
    bl_idname = "bim.close_blend_warning"
    bl_label = "Close Blend Warning"

    def execute(self, context):
        props = tool.Blender.get_bim_props()
        props.has_blend_warning = False
        return {"FINISHED"}

    def draw(self, context):
        self.layout.label(text="Warning: you may experience errors. Really continue?")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SelectURIAttribute(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.select_uri_attribute"
    bl_label = "Select URI Attribute"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select a local file"
    attribute_data_path: bpy.props.StringProperty(name="Data Path")  # pyright: ignore[reportRedeclaration]
    """Full data path to `Attribute`/string property."""
    use_relative_path: bpy.props.BoolProperty(  # pyright: ignore[reportRedeclaration]
        name="Use Relative Path",
        default=False,
    )

    if TYPE_CHECKING:
        attribute_data_path: str
        use_relative_path: bool

    def execute(self, context):
        from bonsai.bim.prop import Attribute

        filepath = tool.Ifc.get_uri(self.filepath, use_relative_path=self.use_relative_path)

        attribute = eval(self.attribute_data_path)
        if isinstance(attribute, Attribute):
            attribute.string_value = filepath
        else:
            bpy_struct_path, _, attr_name = self.attribute_data_path.rpartition(".")
            setattr(eval(bpy_struct_path), attr_name, filepath)
        return {"FINISHED"}


class BIM_OT_multiple_file_selector(bpy.types.Operator, ImportHelper):
    """Open Blender's file explorer to select one or multiple files."""

    bl_idname = "bim.multiple_file_selector"
    bl_label = "Select File(s)"
    bl_options = {"REGISTER", "UNDO"}
    files: bpy.props.CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)
    filter_glob: bpy.props.StringProperty(default="*", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    if TYPE_CHECKING:
        file_props: MultipleFileSelect

    @classmethod
    def poll(cls, context):
        return getattr(context, "file_props", None) is not None

    def execute(self, context):
        dirname = os.path.dirname(self.filepath)
        self.file_props.single_file = self.filepath
        self.file_props.set_file_list(dirname, [f.name for f in self.files])

        return {"FINISHED"}

    def invoke(self, context, event):
        self.file_props = context.file_props
        return ImportHelper.invoke(self, context, event)


class SelectIfcFile(bpy.types.Operator, IFCFileSelector, ImportHelper):
    bl_idname = "bim.select_ifc_file"
    bl_label = "Select IFC File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = f"Select a different IFC file.\n{tool.Blender.operator_invoke_filepath_hotkeys_description}"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)
    filename_ext = ".ifc"

    def execute(self, context):
        if self.is_existing_ifc_file():
            props = tool.Blender.get_bim_props()
            props.ifc_file = self.get_filepath()
            bonsai.bim.handler.loadIfcStore(bpy.context.scene)
            tool.Blender.clear_undo_history()
        return {"FINISHED"}

    def invoke(self, context, event):
        props = tool.Blender.get_bim_props()
        filepath = Path(props.ifc_file)
        res = tool.Blender.operator_invoke_filepath_hotkeys(self, context, event, filepath)
        if res is not None:
            return res
        return ImportHelper.invoke(self, context, event)


# TODO: Unused operator.
# Is there a need for this or 'DIR_PATH' propety subtype does almost the same,
# but also has alt+click?
class SelectDir(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.select_dir"
    bl_label = "Select Directory"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open a file browser to choose the directory"
    data_path: bpy.props.StringProperty(name="Data Path")

    if TYPE_CHECKING:
        data_path: str

    def execute(self, context):
        data, attr = tool.Blender.resolve_data_path_to_data_attr(self.data_path)
        setattr(data, attr, os.path.dirname(self.filepath))
        return {"FINISHED"}

    def invoke(self, context, event):
        return ImportHelper.invoke(self, context, event)


class WinRegistryKeys(Enum):
    __bonsai_key = "bonsai.ifc"
    # Have to list all keys here
    # because .DeleteKey can't remove key that has subkeys.
    BONSAI = rf"Software\Classes\{__bonsai_key}"
    BONSAI_ICON = rf"{BONSAI}\DefaultIcon"
    BONSAI_SHELL = rf"{BONSAI}\shell"
    BONSAI_SHELL_OPEN = rf"{BONSAI}\shell\open"
    BONSAI_COMMAND = rf"{BONSAI}\shell\open\command"
    IFC_EXTENSION = r"Software\Classes\.ifc"
    IFC_EXTENSION_OPEN_WITH = rf"{IFC_EXTENSION}\OpenWihProgids"

    @classmethod
    def get_bonsai_key(cls):
        return cls.__bonsai_key


LIBS_DESKTOP = Path(__file__).parent.parent / "libs" / "desktop"


class FileAssociate(bpy.types.Operator):
    bl_idname = "bim.file_associate"
    bl_label = "Associate Bonsai with *.ifc files"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Creates a Desktop launcher and associates it with IFC files"

    @classmethod
    def poll(cls, context):
        if platform.system() in ("Linux", "Windows"):
            return True
        cls.poll_message_set("Option available only on Windows & Linux.")
        # TODO Darwin
        # https://stackoverflow.com/questions/1082889/how-to-change-filetype-association-in-the-registry
        return False

    def execute(self, context):
        binary_path = bpy.app.binary_path
        if platform.system() == "Linux":
            destdir = os.path.join(os.environ["HOME"], ".local")
            self.install_desktop_linux(src_dir=LIBS_DESKTOP, destdir=destdir, binary_path=binary_path)
        elif platform.system() == "Windows":
            self.install_desktop_windows(binary_path)
        self.report({"INFO"}, "Associations established.")
        return {"FINISHED"}

    def install_desktop_windows(self, binary_path: str) -> None:
        import winreg

        filetype_name = "Bonsai IFC Project"

        # File association code from https://github.com/Victor-IX/Blender-Launcher-V2.
        # Create a ProgID.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WinRegistryKeys.BONSAI.value) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, filetype_name)

        python_expression = """import bpy;
        import sys;
        filepath = sys.argv[sys.argv.index('--') + 1];
        bpy.ops.bim.load_project(filepath=filepath)
        """
        python_expression = "".join(line.strip() for line in python_expression.splitlines())
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WinRegistryKeys.BONSAI_COMMAND.value) as key:
            winreg.SetValueEx(
                key,
                "",
                0,
                winreg.REG_SZ,
                # Pass the file path after '--' to avoid issues with special characters.
                f'"{binary_path}" --python-expr "{python_expression}" -- "%1"',
            )

        # Finally associate, changes take effect immediately, no need to restart explorer.
        # Haven't found any use of setting OpenWihProgids - just adding association makes "Open With" work too.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WinRegistryKeys.IFC_EXTENSION.value) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, WinRegistryKeys.get_bonsai_key())

        # Add an icon.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WinRegistryKeys.BONSAI_ICON.value) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{binary_path}", 0')

    def install_desktop_linux(self, src_dir=None, destdir="/tmp", binary_path="/usr/bin/blender"):
        """Creates linux file assocations and launcher icon"""

        for rel_path in (
            "bin",
            "share/icons/hicolor/128x128/apps",
            "share/icons/hicolor/128x128/mimetypes",
            "share/applications",
            "share/mime/packages",
        ):
            os.makedirs(os.path.join(destdir, rel_path), exist_ok=True)

        shutil.copy(
            os.path.join(src_dir, "bonsai.png"),
            os.path.join(destdir, "share/icons/hicolor/128x128/apps"),
        )
        shutil.copy(
            os.path.join(src_dir, "bonsai.desktop"),
            os.path.join(destdir, "share/applications"),
        )
        shutil.copy(
            os.path.join(src_dir, "bonsai.xml"),
            os.path.join(destdir, "share/mime/packages"),
        )
        shutil.copyfile(
            os.path.join(src_dir, "x-ifc_128x128.png"),
            os.path.join(destdir, "share/icons/hicolor/128x128/mimetypes", "x-ifc.png"),
        )

        # copy and rewrite wrapper script
        with open(os.path.join(src_dir, "bonsai"), "r") as wrapper_template:
            filedata = wrapper_template.read()
            filedata = filedata.replace("#BLENDER_EXE=/opt/blender-3.3/blender", 'BLENDER_EXE="' + binary_path + '"')
        with open(os.path.join(destdir, "bin", "bonsai"), "w") as wrapper:
            wrapper.write(filedata)

        os.chmod(os.path.join(destdir, "bin", "bonsai"), 0o755)

        self.refresh_system_linux(destdir=destdir)

    def refresh_system_linux(self, destdir="/tmp"):
        """Attempt to update mime and desktop databases"""
        try:
            subprocess.call(["update-mime-database", os.path.join(destdir, "share/mime")])
        except:
            pass
        try:
            subprocess.call(["update-desktop-database", os.path.join(destdir, "share/applications")])
        except:
            pass


class FileUnassociate(bpy.types.Operator):
    bl_idname = "bim.file_unassociate"
    bl_label = "Remove Bonsai *.ifc association"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Removes Desktop launcher and unassociates it with IFC files"

    @classmethod
    def poll(cls, context):
        if platform.system() in ("Linux", "Windows"):
            return True
        cls.poll_message_set("Option available only on Windows & Linux.")
        return False

    def execute(self, context):
        if platform.system() == "Linux":
            destdir = os.path.join(os.environ["HOME"], ".local")
            self.uninstall_desktop_linux(destdir=destdir)
        elif platform.system() == "Windows":
            self.uninstall_desktop_windows()

        return {"FINISHED"}

    def uninstall_desktop_windows(self) -> None:
        import winreg

        for key in reversed(WinRegistryKeys):
            key_path = key.value
            # Ignore IFC extension keys as you may never know what subkeys it might have.
            # And removing Bonsai keys is good enough for removing association.
            if key_path.startswith(WinRegistryKeys.IFC_EXTENSION.value):
                continue
            with contextlib.suppress(FileNotFoundError):
                print(f"Removing registry key '{key_path}'.")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)

        # TODO: Keys are deprecated since 25-05-01, remove the cleanup later.
        # Clean up legacy keys, trying to be a good citizen.
        with contextlib.suppress(FileNotFoundError):
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"BLENDERBIM") as key:
                cmd = (
                    "powershell",
                    "-Command",
                    r"Start-Process -Verb RunAs -Wait cmd -ArgumentList '/c reg delete HKCR\BLENDERBIM /f'",
                )
                subprocess.run(cmd, check=True)
                print("Successfully removed deprecated key 'BLENDERBIM'.")
        with contextlib.suppress(FileNotFoundError):
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"BONSAI") as key:
                cmd = (
                    "powershell",
                    "-Command",
                    r"Start-Process -Verb RunAs -Wait cmd -ArgumentList '/c reg delete HKCR\BONSAI /f'",
                )
                subprocess.run(cmd, check=True)
                print("Successfully removed deprecated key 'BONSAI'.")

        self.report({"INFO"}, "Association removed.")

    def uninstall_desktop_linux(self, destdir="/tmp"):
        """Removes linux file assocations and launcher icon"""
        for rel_path in (
            "share/icons/hicolor/128x128/apps/bonsai.png",
            "share/icons/hicolor/128x128/mimetypes/x-ifc.png",
            "share/applications/bonsai.desktop",
            "share/mime/packages/bonsai.xml",
            "bin/bonsai",
            "share/icons/hicolor/128x128/apps/bonsai.png",
            "share/applications/bonsai.desktop",
            "share/mime/packages/bonsai.xml",
            "bin/bonsai",
        ):
            try:
                os.remove(os.path.join(destdir, rel_path))
            except:
                pass

        self.refresh_system_linux(destdir=destdir)

    def refresh_system_linux(self, destdir="/tmp"):
        """Attempt to update mime and desktop databases"""
        try:
            subprocess.call(["update-mime-database", os.path.join(destdir, "share/mime")])
        except:
            pass
        try:
            subprocess.call(["update-desktop-database", os.path.join(destdir, "share/applications")])
        except:
            pass


class CreateMacBonsaiApp(bpy.types.Operator):
    bl_idname = "bim.create_mac_bonsai_app"
    bl_label = "Create Bonsai App to Open .ifc Files."
    bl_options = set()
    bl_description = (
        "Create 'Bonsai' application on Mac.\n\n"
        "To make Mac use Bonsai to open IFC files automatically:\n"
        "- Open context menu on any .ifc file\n"
        "- Open With\n"
        "- Other\n"
        "- Select Bonsai in 'Applications'\n"
        "- Check 'Always Open With'\n"
        "- 'Open'\n"
        "\n"
        "ALT+click to uninstall Bonsai app if it was installed previously."
    )

    uninstall: bpy.props.BoolProperty(options={"SKIP_SAVE"})  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        uninstall: bool

    @classmethod
    def poll(cls, context):
        if platform.system() == "Darwin":
            return True
        cls.poll_message_set("Mac Only.")
        return False

    def invoke(self, context, event):
        self.uninstall = event.alt
        return self.execute(context)

    def execute(self, context):
        # I've tried to create AppleScript that would create this kind of app using Automator,
        # but using poorly document AppleScript was unbearable :(
        # So we just try to create automator app ourselves from a template.

        # Couldn't find a way to automatically establish .ifc to app association,
        # without installing some other app to handle it (e.g. 'duti').
        # So currently we rely on the final user action to select Bonsai in 'Open With'.

        # NOTE: shell script to execute is part of .wflow file.
        app_path = Path("/Applications") / "Bonsai.app"

        if self.uninstall:
            if app_path.exists():
                shutil.rmtree(app_path)
                self.report({"INFO"}, "Bonsai app was successfully removed.")
            else:
                self.report({"WARNING"}, f"Couldn't remove Bonsai app as it's not found at '{app_path}'.")
            return {"FINISHED"}

        if app_path.exists():
            self.report({"WARNING"}, f"Bonsai.app already exists at '{app_path}'.")
            return {"FINISHED"}

        # 1. Create .app bundle structure
        contents = app_path / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"
        for p in (macos, resources):
            p.mkdir(parents=True, exist_ok=True)

        # Copy Automator Application Stub.
        stub_src = Path(
            "/System/Library/CoreServices/Automator Application Stub.app/Contents/MacOS/Automator Application Stub"
        )
        stub_dest = macos / "Automator Application Stub"
        shutil.copy(stub_src, stub_dest)
        stub_dest.chmod(0o755)

        # xml files.
        shutil.copy2(LIBS_DESKTOP / "Mac" / "Info.plist", contents / "Info.plist")
        wflow_template = (LIBS_DESKTOP / "Mac" / "document.wflow").read_text()
        wflow_template = wflow_template.replace("{{BLENDER_BINARY}}", bpy.app.binary_path)
        (contents / "document.wflow").write_text(wflow_template)

        # Convert PNG icon to ICNS.
        png_icon = LIBS_DESKTOP / "bonsai.png"
        icns_icon = app_path / "Contents/Resources/AppIcon.icns"
        subprocess.run(["sips", "-s", "format", "icns", png_icon, "--out", icns_icon], check=True)

        self.report(
            {"INFO"},
            "Bonsai app was successfully created. "
            f"Follow instructions in '{self.bl_label}' description to use Bonsai for .ifc files automatically.",
        )
        return {"FINISHED"}


class OpenUpstream(bpy.types.Operator):
    bl_idname = "bim.open_upstream"
    bl_label = "Open Upstream Reference"
    page: bpy.props.StringProperty()

    def execute(self, context):
        if self.page == "home":
            webbrowser.open("https://bonsaibim.org/")
        elif self.page == "docs":
            webbrowser.open("https://docs.bonsaibim.org/")
        elif self.page == "wiki":
            webbrowser.open("https://wiki.osarch.org/index.php?title=Category:Bonsai")
        elif self.page == "community":
            webbrowser.open("https://community.osarch.org/")
        elif self.page == "fund":
            webbrowser.open("https://opencollective.com/opensourcebim")
        return {"FINISHED"}


class BIM_OT_add_section_plane(bpy.types.Operator):
    """Add a temporary empty object as a section cutaway. Cull all geometry rendering below the empty's local Z axis"""

    bl_idname = "bim.add_section_plane"
    bl_label = "Add Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = self.create_section_obj(context)
        if not self.has_section_override_node():
            self.create_section_compare_node()
            self.create_section_override_node(obj, context)
        else:
            self.append_obj_to_section_override_node(obj)
        self.add_default_material_if_none_exists(context)
        self.override_materials()
        return {"FINISHED"}

    def create_section_obj(self, context):
        section = bpy.data.objects.new("Section", None)
        section.empty_display_type = "SINGLE_ARROW"
        section.empty_display_size = 5
        section.show_in_front = True
        if (
            context.active_object
            and context.active_object.select_get()
            and isinstance(context.active_object.data, bpy.types.Camera)
        ):
            section.matrix_world = (
                context.active_object.matrix_world @ Euler((radians(180.0), 0.0, 0.0), "XYZ").to_matrix().to_4x4()
            )
        else:
            section.rotation_euler = Euler((radians(180.0), 0.0, 0.0), "XYZ")
            section.location = context.scene.cursor.location
        collection = bpy.data.collections.get("Sections")
        if not collection:
            collection = bpy.data.collections.new("Sections")
            context.scene.collection.children.link(collection)
        collection.objects.link(section)
        return section

    def has_section_override_node(self):
        return bpy.data.node_groups.get("Section Override")

    def create_section_compare_node(self):
        group = bpy.data.node_groups.new("Section Compare", type="ShaderNodeTree")
        input_value = group.interface.new_socket(name="Value", in_out="INPUT", socket_type="NodeSocketFloat")
        input_value.default_value = 1.0  # Mandatory multiplier for the last node group
        group.interface.new_socket(name="Vector", in_out="INPUT", socket_type="NodeSocketVector")
        group.interface.new_socket(name="Line Decorator", in_out="INPUT", socket_type="NodeSocketFloat")
        group.interface.new_socket(name="Value", in_out="OUTPUT", socket_type="NodeSocketFloat")
        group.interface.new_socket(name="Line Decorator", in_out="OUTPUT", socket_type="NodeSocketFloat")

        group_input = group.nodes.new(type="NodeGroupInput")
        group_input.location = 0, 50

        separate_xyz = group.nodes.new(type="ShaderNodeSeparateXYZ")
        separate_xyz.location = 200, 0

        greater = group.nodes.new(type="ShaderNodeMath")
        greater.operation = "GREATER_THAN"
        greater.inputs[1].default_value = 0
        greater.location = 400, 0

        compare = group.nodes.new(type="ShaderNodeMath")
        compare.operation = "COMPARE"
        compare.inputs[1].default_value = 0
        compare.inputs[2].default_value = 0.04
        compare.location = 400, -200

        multiply = group.nodes.new(type="ShaderNodeMath")
        multiply.operation = "MULTIPLY"
        multiply.inputs[0].default_value = 1
        multiply.location = 600, 150

        add_line_decorator = group.nodes.new(type="ShaderNodeMath")
        add_line_decorator.operation = "ADD"
        add_line_decorator.location = 600, -200

        multiply_line_decorator = group.nodes.new(type="ShaderNodeMath")
        multiply_line_decorator.operation = "MULTIPLY"
        multiply_line_decorator.location = 800, -200

        group_output = group.nodes.new(type="NodeGroupOutput")
        group_output.location = 1000, 0

        group.links.new(group_input.outputs["Value"], multiply.inputs[0])
        group.links.new(group_input.outputs["Vector"], separate_xyz.inputs[0])
        group.links.new(separate_xyz.outputs[2], greater.inputs[0])
        group.links.new(greater.outputs[0], multiply.inputs[1])
        group.links.new(multiply.outputs[0], group_output.inputs["Value"])
        group.links.new(separate_xyz.outputs[2], compare.inputs[0])
        group.links.new(compare.outputs[0], add_line_decorator.inputs[0])
        group.links.new(group_input.outputs["Line Decorator"], add_line_decorator.inputs[1])
        group.links.new(multiply.outputs[0], multiply_line_decorator.inputs[0])
        group.links.new(add_line_decorator.outputs[0], multiply_line_decorator.inputs[1])
        group.links.new(multiply_line_decorator.outputs[0], group_output.inputs["Line Decorator"])

    def create_section_override_node(self, obj, context):
        group = bpy.data.node_groups.new("Section Override", type="ShaderNodeTree")
        group.interface.new_socket(name="Shader", in_out="INPUT", socket_type="NodeSocketShader")
        group.interface.new_socket(name="Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
        links = group.links
        nodes = group.nodes

        group_input = nodes.new(type="NodeGroupInput")
        group_output = nodes.new(type="NodeGroupOutput")
        group_output.location = 800, 250

        mix_decorator = group.nodes.new(type="ShaderNodeMixShader")
        mix_decorator.name = "Line Decorator Mix"
        # Directly pass input shader when there is no cutaway
        mix_decorator.inputs[0].default_value = 0
        mix_decorator.location = group_output.location - Vector((200, 0))

        mix_section = group.nodes.new(type="ShaderNodeMixShader")
        mix_section.name = "Section Mix"
        # Directly pass input shader when there is no cutaway
        mix_section.inputs[0].default_value = 1
        mix_section.location = mix_decorator.location - Vector((200, 200))

        transparent = nodes.new(type="ShaderNodeBsdfTransparent")
        transparent.location = mix_section.location - Vector((200, 100))

        mix_backfacing = nodes.new(type="ShaderNodeMixShader")
        mix_backfacing.location = mix_section.location - Vector((200, 0))

        group_input.location = mix_backfacing.location - Vector((200, 50))

        backfacing = nodes.new(type="ShaderNodeNewGeometry")
        backfacing.location = mix_backfacing.location + Vector((-200, 200))

        emission = nodes.new(type="ShaderNodeEmission")
        props = tool.Blender.get_bim_props()
        emission.inputs[0].default_value = list(props.section_plane_colour) + [1]
        emission.location = mix_backfacing.location - Vector((200, 150))

        cut_obj = nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        cut_obj.location = backfacing.location - Vector((200, 200))

        section_compare = nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.name = "Last Section Compare"
        section_compare.location = backfacing.location + Vector((0, 200))

        links.new(cut_obj.outputs["Object"], section_compare.inputs[1])
        links.new(backfacing.outputs["Backfacing"], mix_backfacing.inputs[0])
        links.new(group_input.outputs["Shader"], mix_backfacing.inputs[1])
        links.new(emission.outputs["Emission"], mix_backfacing.inputs[2])
        links.new(section_compare.outputs["Value"], mix_section.inputs[0])
        links.new(transparent.outputs[0], mix_section.inputs[1])
        links.new(mix_backfacing.outputs["Shader"], mix_section.inputs[2])
        links.new(section_compare.outputs["Line Decorator"], mix_decorator.inputs[0])
        links.new(mix_section.outputs["Shader"], mix_decorator.inputs[1])
        links.new(mix_decorator.outputs["Shader"], group_output.inputs["Shader"])

    def append_obj_to_section_override_node(self, obj):
        group = bpy.data.node_groups.get("Section Override")
        try:
            last_section_node = next(
                n
                for n in group.nodes
                if isinstance(n, bpy.types.ShaderNodeGroup)
                and n.node_tree.name == "Section Compare"
                and not n.inputs[0].links
            )
            offset = Vector((0, 0))
        except StopIteration:
            last_section_node = group.nodes.get("Section Mix")
            offset = Vector((200, 0))
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.location = last_section_node.location - Vector((200, 0)) - offset

        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        cut_obj.location = last_section_node.location - Vector((400, 150)) - offset

        group.links.new(section_compare.outputs["Value"], last_section_node.inputs[0])
        group.links.new(
            section_compare.outputs["Line Decorator"],
            (
                last_section_node.inputs["Line Decorator"]
                if "Line Decorator" in last_section_node.inputs
                else group.nodes.get("Line Decorator Mix").inputs[0]
            ),
        )
        group.links.new(cut_obj.outputs["Object"], section_compare.inputs[1])

        section_compare.name = "Last Section Compare"

    def add_default_material_if_none_exists(self, context):
        material = bpy.data.materials.get("Section Override")
        if not material:
            material = bpy.data.materials.new("Section Override")
            material.use_nodes = True

        props = tool.Blender.get_bim_props()
        if props.should_section_selected_objects:
            objects = list(context.selected_objects)
        else:
            objects = list(context.visible_objects)

        for obj in objects:
            aggregate = obj.instance_collection
            if aggregate and "IfcRelAggregates/" in aggregate.name:
                for part in aggregate.objects:
                    objects.append(part)
            if not (obj.data and hasattr(obj.data, "materials") and obj.data.materials and obj.data.materials[0]):
                if obj.data and hasattr(obj.data, "materials"):
                    if len(obj.material_slots):
                        obj.material_slots[0].material = material
                    else:
                        obj.data.materials.append(material)

    def override_materials(self):
        override = bpy.data.node_groups.get("Section Override")
        for material in bpy.data.materials:
            material.use_nodes = True
            if material.node_tree.nodes.get("Section Override"):
                continue
            # In EEVEE rendering engine, `blend_mode` is deprecated and replaced by `surface_render_method`
            # https://developer.blender.org/docs/release_notes/4.2/eevee_migration/#materials
            if hasattr(material, "surface_render_method"):
                material.surface_render_method = "DITHERED"
            else:
                material.blend_method = "HASHED"

            # TODO: Find an alternative to `shadow_method` for EEVEE engine
            if hasattr(material, "shadow_method"):
                material.shadow_method = "HASHED"

            material_output = tool.Blender.get_material_node(material, "OUTPUT_MATERIAL", {"is_active_output": True})
            if not material_output:
                continue
            from_socket = material_output.inputs[0].links[0].from_socket
            section_override = material.node_tree.nodes.new(type="ShaderNodeGroup")
            section_override.name = "Section Override"
            section_override.node_tree = override
            material.node_tree.links.new(from_socket, section_override.inputs[0])
            material.node_tree.links.new(section_override.outputs[0], material_output.inputs[0])


class BIM_OT_remove_section_plane(bpy.types.Operator):
    """Remove selected section plane. No effect if executed on a regular object"""

    bl_idname = "bim.remove_section_plane"
    bl_label = "Remove Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object and bpy.data.node_groups.get("Section Override")

    def execute(self, context):
        name = context.active_object.name
        section_override = bpy.data.node_groups.get("Section Override")
        tex_coords = next(
            (
                n
                for n in section_override.nodes
                if isinstance(n, bpy.types.ShaderNodeTexCoord) and n.object and n.object.name == name
            ),
            None,
        )
        if tex_coords is not None:
            section_compare = tex_coords.outputs["Object"].links[0].to_node

            if section_compare.inputs[0].links and section_compare.outputs[0].links:
                previous_section_compare = section_compare.inputs[0].links[0].from_node
                next_section_compare = section_compare.outputs[0].links[0].to_node
                section_override.links.new(previous_section_compare.outputs[0], next_section_compare.inputs[0])
                section_override.links.new(
                    previous_section_compare.outputs[1],
                    (
                        next_section_compare.inputs["Line Decorator"]
                        if "Line Decorator" in next_section_compare.inputs
                        else next_section_compare.inputs[0]
                    ),
                )
                self.offset_previous_nodes(section_compare, offset_x=200)
            section_override.nodes.remove(section_compare)
            section_override.nodes.remove(tex_coords)
            bpy.data.objects.remove(context.active_object)

        return {"FINISHED"}

    def offset_previous_nodes(self, section_compare, offset_x=0, offset_y=0):
        if section_compare.inputs[0].links:
            previous_section_compare = section_compare.inputs[0].links[0].from_node
            previous_section_compare.location += Vector((offset_x, offset_y))
            if previous_section_compare.inputs["Vector"].links:
                previous_section_compare.inputs["Vector"].links[0].from_node.location += Vector((offset_x, offset_y))
            self.offset_previous_nodes(previous_section_compare, offset_x, offset_y)

    def purge_all_section_data(self, context):
        bpy.data.materials.remove(bpy.data.materials.get("Section Override"))
        for material in bpy.data.materials:
            if not material.node_tree:
                continue
            override = material.node_tree.nodes.get("Section Override")
            if not override:
                continue
            material.node_tree.links.new(
                override.inputs[0].links[0].from_socket, override.outputs[0].links[0].to_socket
            )
            material.node_tree.nodes.remove(override)
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Override"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Compare"))
        with context.temp_override(selected_objects=[context.active_object]):
            bpy.ops.object.delete()


class ReloadIfcFile(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.reload_ifc_file"
    bl_label = "Reload IFC File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload an updated IFC file"
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    filename_ext = ".ifc"

    def _execute(self, context):
        import ifcdiff

        old = tool.Ifc.get()
        new: ifcopenshell.file
        new = ifcopenshell.open(self.filepath)

        ifc_diff = ifcdiff.IfcDiff(old, new, relationships=[])
        ifc_diff.diff()

        changed_elements = set([k for k, v in ifc_diff.change_register.items() if "geometry_changed" in v])

        for global_id in ifc_diff.deleted_elements | changed_elements:
            element = tool.Ifc.get().by_guid(global_id)
            obj = tool.Ifc.get_object(element)
            if obj:
                bpy.data.objects.remove(obj)

        # STEP IDs may change, but we assume the GlobalID to be constant
        obj_map = {}
        for obj in bpy.data.objects:
            if obj.library:
                continue
            element = tool.Ifc.get_entity(obj)
            if element and hasattr(element, "GlobalId"):
                obj_map[obj.name] = element.GlobalId

        delta_elements = [new.by_guid(global_id) for global_id in ifc_diff.added_elements | changed_elements]
        tool.Ifc.set(new)

        for obj in bpy.data.objects:
            if obj.library:
                continue
            global_id = obj_map.get(obj.name)
            if global_id:
                try:
                    tool.Ifc.link(new.by_guid(global_id), obj)
                except:
                    # Still prototyping, so things like types definitely won't work
                    print("Could not relink", obj)

        start = time.time()
        logger = logging.getLogger("ImportIFC")
        path_log = tool.Blender.get_data_dir_path("process.log")
        if not os.access(path_log.parent, os.W_OK):
            path_log = os.path.join(
                tempfile.mkdtemp(dir=tool.Blender.get_addon_preferences().tmp_dir or None), "process.log"
            )
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )
        settings = import_ifc.IfcImportSettings.factory(context, self.filepath, logger)
        settings.has_filter = True
        settings.should_filter_spatial_elements = False
        settings.elements = delta_elements
        settings.logger.info("Starting import")
        ifc_importer = import_ifc.IfcImporter(settings)
        ifc_importer.execute()
        settings.logger.info("Import finished in {:.2f} seconds".format(time.time() - start))
        print("Import finished in {:.2f} seconds".format(time.time() - start))

        bim_props = tool.Blender.get_bim_props()
        bim_props.ifc_file = self.filepath
        return {"FINISHED"}


class FetchObjectPassport(bpy.types.Operator):
    bl_idname = "bim.fetch_object_passport"
    bl_label = "Fetch Object Passport"

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        obj = context.active_object
        props = tool.Blender.get_object_bim_props(obj)
        for reference in props.document_references:
            bim_props = tool.Blender.get_bim_props()
            reference = bim_props.document_references[reference.name]
            if reference.location[-6:] == ".blend":
                self.fetch_blender(reference, context)
        return {"FINISHED"}

    def fetch_blender(self, reference, context):
        bpy.ops.wm.link(filename=reference.name, directory=os.path.join(reference.location, "Mesh"))
        context.active_object.data = bpy.data.meshes[reference.name]


def update_enum_property_search_prop(self: "BIM_OT_enum_property_search", context: bpy.types.Context) -> None:
    for i, prop in enumerate(self.collection_names):
        if prop.name == self.dummy_name:
            setattr(context.data, self.prop_name, self.collection_identifiers[i].name)
            predefined_type = self.collection_predefined_types[i].name
            if self.first_launch:
                self.first_launch = False
            else:
                if not self.should_click_ok:
                    # This closes popup immediately, avoiding the need to click "OK".
                    context.window.screen = context.window.screen
            if predefined_type:
                try:
                    setattr(context.data, "ifc_predefined_type", predefined_type)
                except TypeError:  # User clicked on a suggestion, but it's not a predefined type
                    pass
            break


class BIM_OT_enum_property_search(bpy.types.Operator):
    bl_idname = "bim.enum_property_search"
    bl_label = "Search"
    bl_description = "Search For Property"
    bl_options = {"REGISTER", "UNDO"}

    first_launch: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})
    dummy_name: bpy.props.StringProperty(name="Property", update=update_enum_property_search_prop)
    collection_names: bpy.props.CollectionProperty(type=StrProperty)
    collection_identifiers: bpy.props.CollectionProperty(type=StrProperty)
    collection_predefined_types: bpy.props.CollectionProperty(type=StrProperty)
    prop_name: bpy.props.StringProperty()
    should_click_ok: bpy.props.BoolProperty(default=False)
    original_operator_path: bpy.props.StringProperty(name="Original Operator Path", default="", options={"SKIP_SAVE"})
    enable_relating_type_suggestions: bpy.props.BoolProperty(default=True)

    identifiers: list[str]

    if TYPE_CHECKING:
        collection_names: bpy.types.bpy_prop_collection_idprop[StrProperty]
        collection_identifiers: bpy.types.bpy_prop_collection_idprop[StrProperty]
        collection_predefined_types: bpy.types.bpy_prop_collection_idprop[StrProperty]

    def invoke(self, context, event):
        self.clear_collections()
        self.data = context.data
        items = get_enum_items(self.data, self.prop_name, context, original_operator_path=self.original_operator_path)
        if items is None:
            return {"FINISHED"}
        self.add_items_regular(items)
        self.add_items_suggestions()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        # Mandatory to access context.data in update :
        self.layout.context_pointer_set(name="data", data=self.data)
        # NOTE: activate_init don't work with prop_search, so cannot activate field for typing,
        # though it would fit perfectly.
        if self.dummy_name:
            self.layout.label(text=f"Current: {self.dummy_name}")

        self.layout.prop_search(self, "dummy_name", self, "collection_names", text=self.prop_name)

    def execute(self, context):
        return {"FINISHED"}

    def clear_collections(self) -> None:
        self.collection_names.clear()
        self.collection_identifiers.clear()

    def add_item(self, identifier: str, name: str, predefined_type: str = ""):
        self.collection_identifiers.add().name = identifier
        self.collection_names.add().name = name
        self.collection_predefined_types.add().name = predefined_type

    def add_items_regular(
        self,
        items: Iterable[Union[tuple[str, str, str], tuple[str, str, str, int], tuple[str, str, str, str, int], None]],
    ) -> None:
        self.identifiers = []
        current_value = getattr(self.data, self.prop_name)
        for item in items:
            if item is None:  # Used as a separator
                continue
            self.identifiers.append(item[0])
            self.add_item(identifier=item[0], name=item[1])
            if item[0] == current_value:
                self.dummy_name = item[1]  # We found the current enum name

    def add_items_suggestions(self) -> None:
        getter_suggestions = getattr(self.data, "getter_enum_suggestions", None)
        if getter_suggestions is not None:
            mapping = getter_suggestions.get(self.prop_name)
            if mapping is None:
                return
            for key, suggestions in mapping().items():
                if key in self.identifiers:
                    if not isinstance(suggestions, (tuple, list)):
                        suggestions = [suggestions]
                    for suggestion in suggestions:
                        predefined_type = suggestion.get("predefined_type", "NOTDEFINED").upper()
                        name = suggestion.get("name")
                        self.add_item(
                            identifier=key,
                            name=f"{key} > {name if name else predefined_type }",
                            predefined_type=predefined_type,
                        )

        if self.enable_relating_type_suggestions:
            self.add_relating_type_suggestions()

    def add_relating_type_suggestions(self) -> None:
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return

        type_elements = []
        for identifier in self.identifiers:
            # Skip 'Untyped' option for annotation types.
            if identifier == "0":
                continue
            element = ifc_file.by_id(int(identifier))
            if element and element.is_a().endswith("Type"):
                type_elements.append(element)

        for element in type_elements:
            base_name = element.Name or "Unnamed"
            element_step_id = str(element.id())

            attributes = []
            for attr_name in ["Description", "PredefinedType", "ElementType", "ObjectType"]:
                value = getattr(element, attr_name, None)
                if value:
                    attributes.append(value)

            if attributes:
                concatenated_name = f"{base_name} > {' > '.join(attributes)}"
                self.add_item(
                    identifier=element_step_id,
                    name=concatenated_name,
                    predefined_type=element.PredefinedType or "",
                )


class BIM_OT_select_entity(bpy.types.Operator):
    bl_idname = "bim.select_entity"
    bl_label = "Select Entity"
    bl_options = {"REGISTER", "UNDO"}
    ifc_id: bpy.props.IntProperty()
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties) -> str:
        return properties.tooltip

    def execute(self, context):
        element = tool.Ifc.get_entity_by_id(self.ifc_id)
        if not element:
            self.report({"ERROR"}, f"No IFC element found with id #{self.ifc_id}.")
            return {"CANCELLED"}

        obj = tool.Ifc.get_object(element)
        if not isinstance(obj, bpy.types.Object):
            self.report({"ERROR"}, f"The following element is not present in the scene as Blender object: '{element}'.")
            return {"CANCELLED"}

        tool.Blender.set_objects_selection(context, obj, [obj], clear_previous_selection=True)
        return {"FINISHED"}


class BIM_OT_select_entity_by_guid(bpy.types.Operator):
    bl_idname = "bim.select_entity_by_guid"
    bl_label = "Select Entity by Guid"
    bl_description = "Select entity by guid currently saved to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def description(cls, context, properties) -> str:
        assert context.window_manager
        return f"{cls.bl_description}:\n'{context.window_manager.clipboard.strip()}'"

    def execute(self, context):
        assert context.window_manager

        ifc_file = tool.Ifc.get()
        guid = context.window_manager.clipboard.strip()
        try:
            element = ifc_file.by_guid(guid)
        except RuntimeError:
            self.report({"ERROR"}, f"No IFC element found with guid '{guid}'.")
            return {"CANCELLED"}

        obj = tool.Ifc.get_object(element)
        if not isinstance(obj, bpy.types.Object):
            self.report({"ERROR"}, f"The following element is not present in the scene as Blender object: '{element}'.")
            return {"CANCELLED"}

        tool.Blender.select_and_activate_single_object(context, obj)
        self.report({"INFO"}, f"Found and selected element: '{obj.name}'.")
        return {"FINISHED"}


class BIM_OT_select_object(bpy.types.Operator):
    bl_idname = "bim.select_object"
    bl_label = "Select Object"
    bl_options = {"REGISTER", "UNDO"}
    obj_name: bpy.props.StringProperty(description="Object Name To Select")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        tool.Blender.set_objects_selection(context, obj, [obj], clear_previous_selection=True)
        return {"FINISHED"}


class BIM_OT_delete_object(bpy.types.Operator):
    bl_idname = "bim.delete_object"
    bl_label = "Delete Object"
    bl_options = {"REGISTER", "UNDO"}
    obj_name: bpy.props.StringProperty(description="Object Name To Delete")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        with context.temp_override(selected_objects=[obj], active_object=obj):
            bpy.ops.bim.override_object_delete(is_batch=False)
        return {"FINISHED"}


class EditBlenderCollection(bpy.types.Operator):
    bl_idname = "bim.edit_blender_collection"
    bl_label = "Add or Remove Blender Collection Item"
    bl_options = {"REGISTER", "UNDO"}
    option: bpy.props.StringProperty(description="add or remove item from collection")
    collection: bpy.props.StringProperty(description="collection to be edited")
    index: bpy.props.IntProperty(description="index of item to be removed")

    def execute(self, context):
        if self.option == "add":
            getattr(context.bim_prop_group, self.collection).add()
        else:
            getattr(context.bim_prop_group, self.collection).remove(self.index)
        return {"FINISHED"}


class BIM_OT_show_description(bpy.types.Operator):
    bl_idname = "bim.show_description"
    bl_label = "Description"
    attr_name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    url: bpy.props.StringProperty()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=450)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        wrapper = textwrap.TextWrapper(width=80)
        for line in wrapper.wrap(self.attr_name + " : " + self.description):
            layout.label(text=line)
        if self.url:
            url_op = layout.operator("bim.open_uri", icon="URL", text="Online IFC Documentation")
            url_op.uri = self.url

    @classmethod
    def description(cls, context, properties):
        return properties.description


CuttingPlaneData = namedtuple("CuttingPlaneData", ["co", "normal"])


class ClippingPlaneCutWithCappings(bpy.types.Operator):
    bl_idname = "bim.clipping_plane_cut_with_cappings"
    bl_label = "Cut With Clipping Planes"
    bl_description = "Cut selected objects with clipping planes and create cappings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Project.get_project_props()
        cutting_planes = [obj for p in props.clipping_planes if (obj := p.obj)]
        if not cutting_planes:
            self.report({"INFO"}, "No cutting planes found.")
            return {"FINISHED"}
        cutting_planes_data = self.get_cutting_plane_data(cutting_planes)

        wm = context.window_manager
        objects_processed, t0 = 0, time.time()
        wm.progress_begin(0, len(context.selected_objects))
        for obj_i, obj in enumerate(context.selected_objects):
            if not isinstance((mesh := obj.data), bpy.types.Mesh):
                continue

            if obj in cutting_planes:
                continue

            RevertClippingPlaneCut.revert_object_mesh(self, obj)

            # localize matrix to consider object's transform
            ws_to_ls = obj.matrix_world.inverted()
            rotation = ws_to_ls.to_quaternion()

            bm = tool.Blender.get_bmesh_for_mesh(mesh)
            object_changed = False

            for plane_data in cutting_planes_data:
                geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
                plane_co = ws_to_ls @ plane_data.co
                plane_no = rotation @ plane_data.normal
                # clear_outer -> remove everything in direction of the normal
                results = bmesh.ops.bisect_plane(
                    bm,
                    geom=geom,
                    dist=10e-4,
                    plane_co=plane_co,
                    plane_no=plane_no,
                    clear_outer=True,
                )
                edges_to_fill = [e for e in results["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
                object_changed = object_changed or edges_to_fill
                bmesh.ops.contextual_create(bm, geom=edges_to_fill)

            # don't swap mesh if it wasn't affected by any of the cutting planes
            if object_changed:
                temp_mesh = bpy.data.meshes.new("temp_cut")
                tool.Geometry.get_mesh_props(temp_mesh).replaced_mesh = mesh
                for material in mesh.materials:
                    temp_mesh.materials.append(material)
                obj.data = temp_mesh
                tool.Blender.apply_bmesh(temp_mesh, bm, obj)

            objects_processed += 1
            wm.progress_update(obj_i)

        self.report({"INFO"}, f"{objects_processed} processed - {time.time()-t0:.3f} sec")

        return {"FINISHED"}

    def get_cutting_plane_data(self, cutting_planes: list[bpy.types.Object]) -> list[CuttingPlaneData]:
        cutting_planes_data = []

        for obj in cutting_planes:
            cutting_matrix = obj.matrix_world
            plane_data = CuttingPlaneData(cutting_matrix.translation, cutting_matrix.col[2].to_3d())
            cutting_planes_data.append(plane_data)

        return cutting_planes_data

    # NOTE: unused, will be used later for cutting boxes support
    def get_box_cutting_plane_data(self, obj: bpy.types.Object) -> list[CuttingPlaneData]:
        matrix_world = obj.matrix_world
        rotation = matrix_world.to_quaternion()  # avoid scale for normals
        cutting_planes_data = []
        for p in obj.data.polygons:
            plane_data = CuttingPlaneData(matrix_world @ p.center, rotation @ p.normal)
            cutting_planes_data.append(plane_data)
        return cutting_planes_data


class RevertClippingPlaneCut(bpy.types.Operator):
    bl_idname = "bim.revert_clipping_plane_cut"
    bl_label = "Revert Clipping Plane Cut"
    bl_description = "Revert clipping plane cut (switch back to the original mesh)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager

        objects_processed, t0 = 0, time.time()
        wm.progress_begin(0, len(context.selected_objects))
        for obj_i, obj in enumerate(context.selected_objects):
            if obj.type != "MESH":
                continue
            self.revert_object_mesh(obj)
            objects_processed += 1
            wm.progress_update(obj_i)
        wm.progress_end()

        self.report({"INFO"}, f"{objects_processed} processed - {time.time()-t0:.3f} sec")
        return {"FINISHED"}

    def revert_object_mesh(self, obj: bpy.types.Object) -> None:
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        replaced_mesh = tool.Geometry.get_mesh_props(mesh).replaced_mesh
        if replaced_mesh:
            obj.data = replaced_mesh
            tool.Blender.remove_data_block(mesh, do_unlink=False)


class CopyTextToClipboard(bpy.types.Operator):
    bl_idname = "bim.copy_text_to_clipboard"
    bl_label = "Copy Text To Clipboard"
    bl_options = set()

    text: bpy.props.StringProperty(options={"SKIP_SAVE"})

    @classmethod
    def description(cls, context, properties):
        return f"Copy text to clipboard: '{properties.text}'."

    def execute(self, context):
        context.window_manager.clipboard = self.text
        return {"FINISHED"}


class ShowSystemInfo(bpy.types.Operator):
    bl_idname = "bim.show_system_info"
    bl_label = "System Info"
    bl_description = "Show debug information and copy it to the clipboard."
    bl_options = set()

    info_text: bpy.props.StringProperty()

    def execute(self, context):
        # invoke_popup doesn't show a popup, if there's no `execute` method.
        return {"FINISHED"}

    def invoke(self, context, event):
        assert context.window_manager
        # Invoke the bim.copy_debug_information operator to get the info to the clipboard
        bpy.ops.bim.copy_debug_information()
        self.info_text = context.window_manager.clipboard

        return context.window_manager.invoke_popup(self, width=600)

    def draw(self, context):
        assert self.layout
        layout = self.layout
        col = layout.column()

        for line in self.info_text.split("\n"):
            col.label(text=line)

        col.separator()
        col.label(text="(The information has been copied to the clipboard.)")


def update_attribute_search_value(self: "BIM_OT_attribute_search_values", context: bpy.types.Context) -> None:
    should_click_ok = False
    attr_name, attribute_obj = BIM_OT_attribute_search_values.resolve_data_path(self.data_path)

    value = self.search_value
    if self.data_type == "integer":
        value = int(value)
    elif self.data_type == "float":
        value = float(value)

    setattr(attribute_obj, attr_name, value)

    if self.first_launch:
        self.first_launch = False
    else:
        if not should_click_ok:
            # This closes popup immediately, avoiding the need to click "OK".
            context.window.screen = context.window.screen


AttributeSearchDataType = Literal["string", "integer", "float"]


class BIM_OT_attribute_search_values(bpy.types.Operator):
    """Search for attribute values. This implementation is based on bim.enum_property_search"""

    bl_idname = "bim.attribute_search_values"
    bl_label = "Search Attribute Values"
    bl_description = "Search for attribute values used in the elements of the same IFC class."
    bl_options = {"REGISTER", "UNDO"}

    # Required properties.
    attribute_name: bpy.props.StringProperty(name="Attribute Name")
    attribute_ifc_class: bpy.props.StringProperty(name="Attribute IFC Class")
    data_path: bpy.props.StringProperty(name="Data Path")
    data_type: bpy.props.EnumProperty(
        name="Data Type",
        items=[(i, i, "") for i in get_args(AttributeSearchDataType)],
    )

    # Internal properties.
    first_launch: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})
    search_value: bpy.props.StringProperty(
        name="Search",
        description="Search for attribute values",
        update=update_attribute_search_value,
        default="",
        options={"SKIP_SAVE"},
    )
    collection_values: bpy.props.CollectionProperty(type=StrProperty, options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        first_launch: bool
        attribute_name: str
        attribute_ifc_class: str
        data_path: str
        data_type: AttributeSearchDataType
        search_value: str
        collection_values: bpy.types.bpy_prop_collection_idprop[StrProperty]

    @staticmethod
    def resolve_data_path(data_path: str) -> tuple[str, "Attribute"]:
        """Resolve the data path of an object's attribute to get the attribute name and the object."""
        attribute_obj, _, attr_name = data_path.rpartition(".")
        attribute_obj = eval(attribute_obj)
        return attr_name, attribute_obj

    def invoke(self, context, event):
        required_props = (self.attribute_name, self.attribute_ifc_class, self.data_path)
        assert all(required_props), required_props

        attr_name, attribute_obj = self.resolve_data_path(self.data_path)
        self.search_value = str(getattr(attribute_obj, attr_name, ""))

        unique_values = self.get_unique_attribute_values()
        string_values = natsorted(unique_values)

        for value in string_values:
            self.collection_values.add().name = value

        assert context.window_manager
        return context.window_manager.invoke_props_dialog(self)

    def get_unique_attribute_values(self) -> list[str]:
        ifc_file = tool.Ifc.get()
        unique_values: set[str] = set()
        ifc_class = self.attribute_ifc_class

        elements = ifc_file.by_type(ifc_class, include_subtypes=True)

        for element in elements:
            # We check just direct entity attributes and simply check if the attribute exists
            if hasattr(element, self.attribute_name):
                value = getattr(element, self.attribute_name)
                if value is not None:
                    unique_values.add(str(value))

        return list(unique_values)

    def draw(self, context) -> None:
        assert self.layout
        row = self.layout.row()
        row.label(text=f"Select {self.attribute_name} value:")
        row = self.layout.row()
        row.prop_search(
            self,
            "search_value",
            self,
            "collection_values",
            text="",
            results_are_suggestions=True,
        )

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        return {"FINISHED"}


class BIM_OT_attribute_add_subitem(bpy.types.Operator):
    bl_idname = "bim.attribute_add_subitem"
    bl_label = "Add Subitem"
    bl_description = "Add subitem to the current attribute"
    bl_options = {"REGISTER", "UNDO"}

    data_path: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]
    """Full data path."""

    if TYPE_CHECKING:
        data_path: str

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        col: bpy.types.bpy_prop_collection_idprop[StrProperty]
        col = eval(self.data_path)

        attr: Attribute = col.data
        if attr.is_optional and not col:
            attr.is_null = False

        col.add()
        return {"FINISHED"}


class BIM_OT_attribute_remove_subitem(bpy.types.Operator):
    bl_idname = "bim.attribute_remove_subitem"
    bl_label = "Add Subitem"
    bl_description = "Add subitem to the current attribute"
    bl_options = {"REGISTER", "UNDO"}

    data_path: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]
    """Full data path."""
    index: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        data_path: str
        index: int

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        col: bpy.types.bpy_prop_collection_idprop[StrProperty]
        col = eval(self.data_path)
        col.remove(self.index)

        attr: Attribute = col.data
        if attr.is_optional and not col:
            attr.is_null = True

        return {"FINISHED"}
