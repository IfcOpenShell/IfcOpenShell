# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
import blenderbim.tool as tool
import blenderbim.core.document as core
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.document.data import Data


class LoadProjectDocuments(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_project_documents"
    bl_label = "Load Project Documents"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_project_documents(tool.Document)


class LoadDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_document"
    bl_label = "Load Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def _execute(self, context):
        core.load_document(tool.Document, document=tool.Ifc.get().by_id(self.document))


class LoadParentDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_parent_document"
    bl_label = "Load Parent Document"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_parent_document(tool.Document)


class DisableDocumentEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_document_editing_ui"
    bl_label = "Disable Document Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_document_editing_ui(tool.Document)


class EnableEditingDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_document"
    bl_label = "Enable Editing Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_document(tool.Document, document=tool.Ifc.get().by_id(self.document))


class DisableEditingDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_document"
    bl_label = "Disable Editing Document"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_document(tool.Document)


class AddInformation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_information"
    bl_label = "Add Information"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_information(tool.Ifc, tool.Document)


class AddDocumentReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_reference(tool.Ifc, tool.Document)


class EditDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_document"
    bl_label = "Edit Information"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMDocumentProperties
        core.edit_document(tool.Ifc, tool.Document, document=tool.Ifc.get().by_id(props.active_document_id))


class RemoveDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_document"
    bl_label = "Remove Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_document(tool.Ifc, tool.Document, document=tool.Ifc.get().by_id(self.document))


class AssignDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_document"
    bl_label = "Assign Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def _execute(self, context):
        document = tool.Ifc.get().by_id(self.document)
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.assign_document(tool.Ifc, product=element, document=document)


class UnassignDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_document"
    bl_label = "Unassign Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def _execute(self, context):
        document = tool.Ifc.get().by_id(self.document)
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.unassign_document(tool.Ifc, product=element, document=document)
