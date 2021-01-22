import bpy
import json
import blenderbim.bim.module.document.add_information as add_information
import blenderbim.bim.module.document.add_reference as add_reference
import blenderbim.bim.module.document.edit_information as edit_information
import blenderbim.bim.module.document.edit_reference as edit_reference
import blenderbim.bim.module.document.remove_document as remove_document
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.document.data import Data


class LoadInformation(bpy.types.Operator):
    bl_idname = "bim.load_information"
    bl_label = "Load Information"

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        while len(props.documents) > 0:
            props.documents.remove(0)
        for information_id, information in Data.information.items():
            new = props.documents.add()
            new.name = information["Name"] or "Unnamed"
            new.identification = information["Identification"] or "*"
            new.ifc_definition_id = information_id
        props.is_editing = "information"
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class LoadDocumentReferences(bpy.types.Operator):
    bl_idname = "bim.load_document_references"
    bl_label = "Load Document References"

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        while len(props.documents) > 0:
            props.documents.remove(0)
        for reference_id, reference in Data.references.items():
            new = props.documents.add()
            new.name = reference["Name"] or "Unnamed"
            new.identification = reference["Identification"] or "*"
            new.ifc_definition_id = reference_id
        props.is_editing = "reference"
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class DisableDocumentEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_document_editing_ui"
    bl_label = "Disable Document Editing UI"

    def execute(self, context):
        context.scene.BIMDocumentProperties.is_editing = ""
        bpy.ops.bim.disable_editing_document()
        return {"FINISHED"}


class EnableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.enable_editing_document"
    bl_label = "Enable Editing Document"
    document: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        while len(props.document_attributes) > 0:
            props.document_attributes.remove(0)

        if props.is_editing == "information":
            data = Data.information[self.document]
            ifc_class = "IfcDocumentInformation"
        elif props.is_editing == "reference":
            data = Data.references[self.document]
            ifc_class = "IfcDocumentReference"

        for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
                continue
            new = props.document_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            if "<string>" in data_type:
                new.string_value = "" if new.is_null else data[attribute.name()]
                new.data_type = "string"
            elif "<enumeration" in data_type:
                new.enum_items = json.dumps(attribute.type_of_attribute().declared_type().enumeration_items())
                new.data_type = "enum"
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_document_id = self.document
        return {"FINISHED"}


class DisableEditingDocument(bpy.types.Operator):
    bl_idname = "bim.disable_editing_document"
    bl_label = "Disable Editing Document"

    def execute(self, context):
        context.scene.BIMDocumentProperties.active_document_id = 0
        return {"FINISHED"}


class AddInformation(bpy.types.Operator):
    bl_idname = "bim.add_information"
    bl_label = "Add Information"

    def execute(self, context):
        result = add_information.Usecase(IfcStore.get_file()).execute()
        Data.load()
        bpy.ops.bim.load_information()
        bpy.ops.bim.enable_editing_document(document=result.id())
        return {"FINISHED"}


class AddDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"

    def execute(self, context):
        result = add_reference.Usecase(IfcStore.get_file()).execute()
        Data.load()
        bpy.ops.bim.load_document_references()
        bpy.ops.bim.enable_editing_document(document=result.id())
        return {"FINISHED"}


class EditInformation(bpy.types.Operator):
    bl_idname = "bim.edit_information"
    bl_label = "Edit Information"

    def execute(self, context):
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
        edit_information.Usecase(
            self.file, {"information": self.file.by_id(props.active_document_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.load_information()
        return {"FINISHED"}


class EditDocumentReference(bpy.types.Operator):
    bl_idname = "bim.edit_document_reference"
    bl_label = "Edit Document Reference"

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        attributes = {}
        for attribute in props.document_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        edit_reference.Usecase(
            self.file, {"reference": self.file.by_id(props.active_document_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.load_document_references()
        return {"FINISHED"}


class RemoveDocument(bpy.types.Operator):
    bl_idname = "bim.remove_document"
    bl_label = "Remove Document"
    document: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMDocumentProperties
        self.file = IfcStore.get_file()
        remove_document.Usecase(self.file, {"document": self.file.by_id(self.document)}).execute()
        Data.load()
        if props.is_editing == "information":
            bpy.ops.bim.load_information()
        elif props.is_editing == "reference":
            bpy.ops.bim.load_document_references()
        return {"FINISHED"}
