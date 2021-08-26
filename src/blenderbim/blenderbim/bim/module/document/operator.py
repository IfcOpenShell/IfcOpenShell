
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

import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.document.data import Data


class LoadInformation(bpy.types.Operator):
    bl_idname = "bim.load_information"
    bl_label = "Load Information"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMDocumentProperties
        props.documents.clear()
        for information_id, information in Data.information.items():
            new = props.documents.add()
            new.name = information["Name"] or "Unnamed"
            if self.file.schema == "IFC2X3":
                new.identification = information["DocumentId"] or "*"
            else:
                new.identification = information["Identification"] or "*"
            new.ifc_definition_id = information_id
        props.is_editing = "information"
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class LoadDocumentReferences(bpy.types.Operator):
    bl_idname = "bim.load_document_references"
    bl_label = "Load Document References"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMDocumentProperties
        props.documents.clear()
        for reference_id, reference in Data.references.items():
            new = props.documents.add()
            new.name = reference["Name"] or "Unnamed"
            if self.file.schema == "IFC2X3":
                new.identification = reference["ItemReference"] or "*"
            else:
                new.identification = reference["Identification"] or "*"
            new.ifc_definition_id = reference_id
        props.is_editing = "reference"
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class DisableDocumentEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_document_editing_ui"
    bl_label = "Disable Document Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMDocumentProperties.is_editing = ""
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class EnableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.enable_editing_document"
    bl_label = "Enable Editing Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        props.document_attributes.clear()

        if props.is_editing == "information":
            data = Data.information[self.document]
            ifc_class = "IfcDocumentInformation"
        elif props.is_editing == "reference":
            data = Data.references[self.document]
            ifc_class = "IfcDocumentReference"

        for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.document_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_document_id = self.document
        return {"FINISHED"}


class DisableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.disable_editing_document"
    bl_label = "Disable Editing Document"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMDocumentProperties.active_document_id = 0
        return {"FINISHED"}


class AddInformation(bpy.types.Operator):
    bl_idname = "bim.add_information"
    bl_label = "Add Information"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("document.add_information", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_information()
        bpy.ops.bim.enable_editing_document(document=result.id())
        return {"FINISHED"}


class AddDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("document.add_reference", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_document_references()
        bpy.ops.bim.enable_editing_document(document=result.id())
        return {"FINISHED"}


class EditInformation(bpy.types.Operator):
    bl_idname = "bim.edit_information"
    bl_label = "Edit Information"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMDocumentProperties
        attributes = {}
        for attribute in props.document_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            elif attribute.enum_items:
                attributes[attribute.name] = attribute.enum_value
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "document.edit_information",
            self.file,
            **{"information": self.file.by_id(props.active_document_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_information()
        return {"FINISHED"}


class EditDocumentReference(bpy.types.Operator):
    bl_idname = "bim.edit_document_reference"
    bl_label = "Edit Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMDocumentProperties
        attributes = {}
        for attribute in props.document_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "document.edit_reference",
            self.file,
            **{"reference": self.file.by_id(props.active_document_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_document_references()
        return {"FINISHED"}


class RemoveDocument(bpy.types.Operator):
    bl_idname = "bim.remove_document"
    bl_label = "Remove Document"
    bl_options = {"REGISTER", "UNDO"}
    document: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMDocumentProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("document.remove_document", self.file, **{"document": self.file.by_id(self.document)})
        Data.load(IfcStore.get_file())
        if props.is_editing == "information":
            bpy.ops.bim.load_information()
        elif props.is_editing == "reference":
            bpy.ops.bim.load_document_references()
        return {"FINISHED"}


class EnableAssigningDocument(bpy.types.Operator):
    bl_idname = "bim.enable_assigning_document"
    bl_label = "Enable Assigning Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectDocumentProperties
        if props.available_document_types == "IfcDocumentInformation":
            bpy.ops.bim.load_information()
        elif props.available_document_types == "IfcDocumentReference":
            bpy.ops.bim.load_document_references()
        props.is_adding = props.available_document_types
        return {"FINISHED"}


class DisableAssigningDocument(bpy.types.Operator):
    bl_idname = "bim.disable_assigning_document"
    bl_label = "Disable Assigning Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectDocumentProperties
        props.is_adding = ""
        return {"FINISHED"}


class AssignDocument(bpy.types.Operator):
    bl_idname = "bim.assign_document"
    bl_label = "Assign Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            obj_id = obj.BIMObjectProperties.ifc_definition_id
            if not obj_id:
                continue
            ifcopenshell.api.run(
                "document.assign_document",
                self.file,
                **{
                    "product": self.file.by_id(obj_id),
                    "document": self.file.by_id(self.document),
                }
            )
            Data.load(self.file, obj_id)
        return {"FINISHED"}


class UnassignDocument(bpy.types.Operator):
    bl_idname = "bim.unassign_document"
    bl_label = "Unassign Document"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            obj_id = obj.BIMObjectProperties.ifc_definition_id
            if not obj_id:
                continue
            ifcopenshell.api.run(
                "document.unassign_document",
                self.file,
                **{
                    "product": self.file.by_id(obj_id),
                    "document": self.file.by_id(self.document),
                }
            )
            Data.load(self.file, obj_id)
        return {"FINISHED"}
