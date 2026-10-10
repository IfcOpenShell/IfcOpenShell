# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from pathlib import Path
from typing import TYPE_CHECKING

import bpy
from bpy_extras.io_utils import ImportHelper

import bonsai.tool as tool
from bonsai.tool.linked_reference import SUPPORTED_SUFFIXES, LinkedReferenceError


class LinkReference(bpy.types.Operator, ImportHelper, tool.Ifc.Operator):
    bl_idname = "bim.link_reference"
    bl_label = "Link Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Link an external .svg or .dxf file as snappable background reference geometry.\n\n"
        "The file is not stored in the IFC model, only a document reference to it"
    )

    filter_glob: bpy.props.StringProperty(default="*.svg;*.dxf", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path",
        description="Whether to store the linked file path relative to the currently opened IFC file",
        default=False,
    )

    if TYPE_CHECKING:
        filepath: str
        filter_glob: str
        use_relative_path: bool

    def draw(self, context):
        assert self.layout
        if tool.Ifc.get() and Path(tool.Ifc.get_path()).is_file():
            self.layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False

    def _execute(self, context):
        filepath = Path(self.filepath)
        if filepath.suffix.lower() not in SUPPORTED_SUFFIXES:
            self.report({"ERROR"}, f"Unsupported file format '{filepath.suffix}', expected .svg or .dxf.")
            return {"CANCELLED"}
        if not filepath.is_file():
            self.report({"ERROR"}, f"File does not exist: '{filepath}'.")
            return {"CANCELLED"}

        props = tool.LinkedReference.get_props()
        uri = tool.Ifc.get_uri(filepath, use_relative_path=self.use_relative_path)
        if any(link.filepath == uri for link in props.references):
            self.report({"ERROR"}, f"'{uri}' is already linked.")
            return {"CANCELLED"}

        link = props.references.add()
        link.name = filepath.name
        link.filepath = uri
        if tool.Ifc.get():
            link.ifc_definition_id = tool.LinkedReference.add_document_reference(uri).id()
        index = len(props.references) - 1
        props.active_reference_index = index
        try:
            bpy.ops.bim.load_linked_reference(reference_index=index)
        finally:
            # A file that cannot be imported should not leave a dead entry.
            if not props.references[index].is_loaded:
                tool.LinkedReference.remove_document_reference(props.references[index])
                props.references.remove(index)
                props.active_reference_index = min(props.active_reference_index, len(props.references) - 1)


class UnlinkReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_reference"
    bl_label = "Unlink Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the linked reference, its imported geometry and its document reference"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def _execute(self, context):
        props = tool.LinkedReference.get_props()
        link = props.references[self.reference_index]
        if link.is_loaded:
            tool.LinkedReference.unload_link(link)
        tool.LinkedReference.remove_document_reference(link)
        props.references.remove(self.reference_index)
        props.active_reference_index = min(props.active_reference_index, len(props.references) - 1)


class LoadLinkedReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_linked_reference"
    bl_label = "Load Linked Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Import the linked file as geometry at its stored placement"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def _execute(self, context):
        link = tool.LinkedReference.get_props().references[self.reference_index]
        if link.is_loaded:
            return
        try:
            anchor = tool.LinkedReference.load_link(link)
        except LinkedReferenceError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        tool.Blender.select_and_activate_single_object(context, anchor)


class UnloadLinkedReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unload_linked_reference"
    bl_label = "Unload Linked Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the imported geometry, keeping the link and its placement"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def _execute(self, context):
        link = tool.LinkedReference.get_props().references[self.reference_index]
        tool.LinkedReference.unload_link(link)


class RefreshLinkedReference(bpy.types.Operator):
    bl_idname = "bim.refresh_linked_reference"
    bl_label = "Refresh Linked Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Re-import the linked file from disk, keeping the current placement"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def execute(self, context):
        link = tool.LinkedReference.get_props().references[self.reference_index]
        try:
            tool.LinkedReference.refresh_link(link)
        except LinkedReferenceError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return {"FINISHED"}


class SelectLinkedReferenceHandle(bpy.types.Operator):
    bl_idname = "bim.select_linked_reference_handle"
    bl_label = "Select Linked Reference Handle"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select the anchor empty to move, rotate or scale the linked reference"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def execute(self, context):
        link = tool.LinkedReference.get_props().references[self.reference_index]
        anchor = tool.LinkedReference.get_anchor(link)
        if anchor is None:
            self.report({"ERROR"}, "Linked reference is not loaded.")
            return {"CANCELLED"}
        tool.Blender.select_and_activate_single_object(context, anchor)
        return {"FINISHED"}


class ToggleLinkedReferenceVisibility(bpy.types.Operator):
    bl_idname = "bim.toggle_linked_reference_visibility"
    bl_label = "Toggle Linked Reference Visibility"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Hide or show the linked reference geometry in the viewport"

    reference_index: bpy.props.IntProperty(name="Reference Index")

    if TYPE_CHECKING:
        reference_index: int

    def execute(self, context):
        link = tool.LinkedReference.get_props().references[self.reference_index]
        anchor = tool.LinkedReference.get_anchor(link)
        if anchor is None:
            self.report({"ERROR"}, "Linked reference is not loaded.")
            return {"CANCELLED"}
        hide = not anchor.hide_viewport
        anchor.hide_viewport = hide
        for obj in anchor.children:
            obj.hide_viewport = hide
        return {"FINISHED"}
