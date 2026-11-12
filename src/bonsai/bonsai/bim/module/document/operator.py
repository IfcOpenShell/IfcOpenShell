# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

import json

import bpy
import ifcopenshell.util.element

import bonsai.core.document as core
import bonsai.tool as tool
from bonsai.bim.module.document.data import ObjectDocumentData


class LoadProjectDocuments(bpy.types.Operator):
    bl_idname = "bim.load_project_documents"
    bl_label = "Load Project Documents"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_project_documents(tool.Document)
        return {"FINISHED"}


class DisableDocumentEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_document_editing_ui"
    bl_label = "Disable Document Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_document_editing_ui(tool.Document)
        return {"FINISHED"}


class DisableObjectDocumentEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_object_document_editing_ui"
    bl_label = "Disable Object Document Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_object_document_editing_ui(tool.Document)
        return {"FINISHED"}


class EnableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.enable_editing_document"
    bl_label = "Enable Editing Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_document(tool.Document, ifc_document=tool.Ifc.get().by_id(self.document))
        return {"FINISHED"}


class DisableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.disable_editing_document"
    bl_label = "Disable Editing Document"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_document(tool.Document)
        return {"FINISHED"}


class AddInformation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_information"
    bl_label = "Add Information"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Document.get_document_props()
        parent = None
        if props.active_document:
            selected_document = props.active_document

            if selected_document.document_type == "PROJECT":
                parent = tool.Ifc.get().by_type("IfcProject")[0]
            elif selected_document.document_type == "INFORMATION":
                parent = tool.Ifc.get().by_id(selected_document.ifc_definition_id)
            elif selected_document.document_type == "REFERENCE":
                self.report({"ERROR"}, "Cannot add an information element as a child of a reference element")
                return {"CANCELLED"}
        else:
            parent = tool.Ifc.get().by_type("IfcProject")[0]

        core.add_information(tool.Ifc, tool.Document, parent)

        expanded_docs = []
        try:
            expanded_docs = json.loads(props.json_string)
        except (AttributeError, json.JSONDecodeError):
            pass

        if parent and parent.is_a("IfcDocumentInformation"):
            if parent.id() not in expanded_docs:
                expanded_docs.append(parent.id())

        props.json_string = json.dumps(expanded_docs)
        bpy.ops.bim.load_project_documents()


class AddDocumentReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Document.get_document_props()

        if not props.active_document:
            self.report({"ERROR"}, "No document selected")
            return {"CANCELLED"}

        selected_document = props.active_document

        if selected_document.document_type != "INFORMATION":
            self.report({"ERROR"}, "Cannot add a reference to a document that is not an information element")
            return {"CANCELLED"}

        parent = tool.Ifc.get().by_id(selected_document.ifc_definition_id)

        props.document_attributes.clear()
        core.add_reference(tool.Ifc, tool.Document)
        expanded_docs = []
        try:
            expanded_docs = json.loads(props.json_string)
        except (AttributeError, json.JSONDecodeError):
            pass

        if parent.id() not in expanded_docs:
            expanded_docs.append(parent.id())
            props.json_string = json.dumps(expanded_docs)

        bpy.ops.bim.load_project_documents()


class EditDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_document"
    bl_label = "Edit Information"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Document.get_document_props()
        if props.active_document_id:
            core.edit_document(tool.Ifc, tool.Document, ifc_document=tool.Ifc.get().by_id(props.active_document_id))
            props.active_document_id = 0


class RemoveDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_document"
    bl_label = "Remove Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_document(tool.Ifc, tool.Document, ifc_document=tool.Ifc.get().by_id(self.document))


class AssignDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_document"
    bl_label = "Assign Document"
    bl_description = "Assign active document to the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def _execute(self, context):
        objs = [bpy.data.objects[self.obj]] if self.obj else tool.Blender.get_selected_objects()
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.assign_document(tool.Ifc, product=element, ifc_document=tool.Ifc.get().by_id(self.document))

        tool.Document.update_document_objects(self.document)
        ObjectDocumentData.load()
        return {"FINISHED"}


class UnassignDocument(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_document"
    bl_label = "Unassign Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def _execute(self, context):
        objs = [bpy.data.objects.get(self.obj)] if self.obj else tool.Blender.get_selected_objects()
        for obj in objs:
            if obj:
                element = tool.Ifc.get_entity(obj)
                if element:
                    core.unassign_document(tool.Ifc, product=element, ifc_document=tool.Ifc.get().by_id(self.document))

        props = tool.Document.get_document_props()
        active_document_id = None
        if props.active_document:
            active_document_id = props.active_document.ifc_definition_id

        if active_document_id and active_document_id != self.document:
            tool.Document.update_document_objects(active_document_id)
        else:
            tool.Document.update_document_objects()

        ObjectDocumentData.load()
        return {"FINISHED"}


class SelectDocumentObjects(bpy.types.Operator):
    bl_idname = "bim.select_document_objects"
    bl_label = "Select Document Objects"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty(name="Document ID", default=0)

    def execute(self, context):
        if not self.document or not (relating_document := tool.Ifc.get_entity_by_id(self.document)):
            self.report({"INFO"}, f"No document found by id '{self.document}'.")
            return {"FINISHED"}

        i = 0
        for element in ifcopenshell.util.element.get_referenced_elements(relating_document):
            obj = tool.Ifc.get_object(element)
            if not obj or obj not in context.selectable_objects:
                continue
            obj.select_set(True)
            i += 1
        self.report({"INFO"}, f"{i} objects selected.")
        return {"FINISHED"}


class LoadObjectDocuments(bpy.types.Operator):
    bl_idname = "bim.load_object_documents"
    bl_label = "Load Object Documents"
    bl_description = "Load documents to assign to the selected object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_project_documents(tool.Document)

        props = tool.Document.get_document_props()
        props.is_object_editing = True
        ObjectDocumentData.load()
        return {"FINISHED"}


class OpenIFCDocument(bpy.types.Operator):
    bl_idname = "bim.open_ifc_document"
    bl_label = "Open IFC Document"
    bl_description = "Open the IFC document in a new Blender instance and load the project"
    bl_options = {"REGISTER", "UNDO"}

    uri: bpy.props.StringProperty(name="URI")

    def execute(self, context):
        import os
        import subprocess

        if not self.uri or not self.uri.lower().startswith("file://"):
            self.report({"ERROR"}, "Only local file:// URIs are supported")
            return {"CANCELLED"}

        filepath = self.uri[7:]

        if not os.path.exists(filepath):
            self.report({"ERROR"}, f"File not found: {filepath}")
            return {"CANCELLED"}

        blender_path = bpy.app.binary_path
        args = [
            blender_path,
            "--python-expr",
            "import bpy; bpy.ops.bim.load_project(filepath='{}')".format(filepath),
        ]
        subprocess.Popen(args)
        self.report({"INFO"}, f"Opening {filepath} in a new Blender instance")

        return {"FINISHED"}


class ToggleDocument(bpy.types.Operator):
    bl_idname = "bim.toggle_document"
    bl_label = "Toggle Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()
    option: bpy.props.StringProperty()

    def execute(self, context):
        expanded_documents = []
        props = tool.Document.get_document_props()
        try:
            expanded_documents = json.loads(props.json_string)
        except (AttributeError, json.JSONDecodeError):
            expanded_documents = []

        document_id = self.document

        document = tool.Ifc.get().by_id(document_id)
        if document:
            if self.option == "Expand" and document_id not in expanded_documents:
                expanded_documents.append(document_id)
            elif self.option == "Collapse" and document_id in expanded_documents:
                expanded_documents.remove(document_id)

        props.json_string = json.dumps(expanded_documents)
        bpy.ops.bim.load_project_documents()
        return {"FINISHED"}
