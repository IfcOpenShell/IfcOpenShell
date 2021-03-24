import bpy
import json
import ifcopenshell.util.attribute
import ifcopenshell.api.document.add_information as add_information
import ifcopenshell.api.document.add_reference as add_reference
import ifcopenshell.api.document.edit_information as edit_information
import ifcopenshell.api.document.edit_reference as edit_reference
import ifcopenshell.api.document.remove_document as remove_document
import ifcopenshell.api.document.assign_document as assign_document
import ifcopenshell.api.document.unassign_document as unassign_document
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.document.data import Data


class LoadInformation(bpy.types.Operator):
    bl_idname = "bim.load_information"
    bl_label = "Load Information"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMDocumentProperties
        while len(props.documents) > 0:
            props.documents.remove(0)
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

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMDocumentProperties
        while len(props.documents) > 0:
            props.documents.remove(0)
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

    def execute(self, context):
        context.scene.BIMDocumentProperties.active_document_id = 0
        return {"FINISHED"}


class AddInformation(bpy.types.Operator):
    bl_idname = "bim.add_information"
    bl_label = "Add Information"

    def execute(self, context):
        result = add_information.Usecase(IfcStore.get_file()).execute()
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_information()
        bpy.ops.bim.enable_editing_document(document=result.id())
        return {"FINISHED"}


class AddDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"

    def execute(self, context):
        result = add_reference.Usecase(IfcStore.get_file()).execute()
        Data.load(IfcStore.get_file())
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
        Data.load(IfcStore.get_file())
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
        Data.load(IfcStore.get_file())
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
        Data.load(IfcStore.get_file())
        if props.is_editing == "information":
            bpy.ops.bim.load_information()
        elif props.is_editing == "reference":
            bpy.ops.bim.load_document_references()
        return {"FINISHED"}


class EnableAssigningDocument(bpy.types.Operator):
    bl_idname = "bim.enable_assigning_document"
    bl_label = "Enable Assigning Document"
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
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectDocumentProperties
        props.is_adding = ""
        return {"FINISHED"}


class AssignDocument(bpy.types.Operator):
    bl_idname = "bim.assign_document"
    bl_label = "Assign Document"
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        assign_document.Usecase(self.file, {
            "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
            "document": self.file.by_id(self.document)
        }).execute()
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UnassignDocument(bpy.types.Operator):
    bl_idname = "bim.unassign_document"
    bl_label = "Unassign Document"
    obj: bpy.props.StringProperty()
    document: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        unassign_document.Usecase(self.file, {
            "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
            "document": self.file.by_id(self.document)
        }).execute()
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}
