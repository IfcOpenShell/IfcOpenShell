import bpy
import json
import blenderbim.bim.module.classification.add_classification as add_classification
import blenderbim.bim.module.classification.remove_classification as remove_classification
import blenderbim.bim.module.classification.edit_classification as edit_classification
import blenderbim.bim.module.classification.add_reference as add_reference
import blenderbim.bim.module.classification.remove_reference as remove_reference
import blenderbim.bim.module.classification.edit_reference as edit_reference
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.classification.data import Data
from blenderbim.bim.module.classification.prop import getClassifications, getReferences


class LoadClassificationLibrary(bpy.types.Operator):
    bl_idname = "bim.load_classification_library"
    bl_label = "Load Classification Library"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        Data.load_library(self.filepath)
        getClassifications(self, context)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AddClassification(bpy.types.Operator):
    bl_idname = "bim.add_classification"
    bl_label = "Add Classification"

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        add_classification.Usecase(
            IfcStore.get_file(), {"classification": Data.library_file.by_id(int(props.available_classifications))}
        ).execute()
        Data.load()
        return {"FINISHED"}


class EnableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification"
    bl_label = "Enable Editing Classification"
    classification: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        while len(props.classification_attributes) > 0:
            props.classification_attributes.remove(0)
        classification_data = Data.classifications[self.classification]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcClassification").all_attributes():
            new = props.classification_attributes.add()
            new.name = attribute.name()
            new.is_null = classification_data[attribute.name()] is None
            new.is_optional = attribute.optional()
            if attribute.name() == "ReferenceTokens":
                new.string_value = "" if new.is_null else json.dumps(classification_data[attribute.name()])
            else:
                new.string_value = "" if new.is_null else classification_data[attribute.name()]
        props.active_classification_id = self.classification
        return {"FINISHED"}


class DisableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification"
    bl_label = "Disable Editing Classification"

    def execute(self, context):
        context.scene.BIMClassificationProperties.active_classification_id = 0
        return {"FINISHED"}


class RemoveClassification(bpy.types.Operator):
    bl_idname = "bim.remove_classification"
    bl_label = "Remove Classification"
    classification: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_classification.Usecase(self.file, {"classification": self.file.by_id(self.classification)}).execute()
        Data.load()
        return {"FINISHED"}


class EditClassification(bpy.types.Operator):
    bl_idname = "bim.edit_classification"
    bl_label = "Edit Classification"

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        attributes = {}
        for attribute in props.classification_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            elif attribute.name == "ReferenceTokens":
                attributes[attribute.name] = json.loads(attribute.string_value)
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        edit_classification.Usecase(
            self.file, {"classification": self.file.by_id(props.active_classification_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.disable_editing_classification()
        return {"FINISHED"}


class EnableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification_reference"
    bl_label = "Enable Editing Classification Reference"
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMClassificationReferenceProperties
        while len(props.reference_attributes) > 0:
            props.reference_attributes.remove(0)
        reference_data = Data.references[self.reference]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcClassificationReference").all_attributes():
            if attribute.name() == "ReferencedSource":
                continue
            new = props.reference_attributes.add()
            new.name = attribute.name()
            new.is_null = reference_data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.string_value = "" if new.is_null else reference_data[attribute.name()]
        props.active_reference_id = self.reference
        return {"FINISHED"}


class DisableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification_reference"
    bl_label = "Disable Editing Classification Reference"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMClassificationReferenceProperties.active_reference_id = 0
        return {"FINISHED"}


class RemoveClassificationReference(bpy.types.Operator):
    bl_idname = "bim.remove_classification_reference"
    bl_label = "Remove Classification Reference"
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        remove_reference.Usecase(
            self.file,
            {
                "reference": self.file.by_id(self.reference),
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
            },
        ).execute()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        Data.load()
        return {"FINISHED"}


class EditClassificationReference(bpy.types.Operator):
    bl_idname = "bim.edit_classification_reference"
    bl_label = "Edit Classification Reference"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMClassificationReferenceProperties
        attributes = {}
        for attribute in props.reference_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        edit_reference.Usecase(
            self.file, {"reference": self.file.by_id(props.active_reference_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.disable_editing_classification_reference()
        return {"FINISHED"}


class AddClassificationReference(bpy.types.Operator):
    bl_idname = "bim.add_classification_reference"
    bl_label = "Add Classification Reference"
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()

        classification = None

        props = context.scene.BIMClassificationProperties
        classification_name = Data.library_classifications[int(props.available_classifications)]
        for classification_id, classification in Data.classifications.items():
            if classification["Name"] == classification_name:
                classification = self.file.by_id(classification_id)
                break

        add_reference.Usecase(
            self.file,
            {
                "reference": Data.library_file.by_id(self.reference),
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "classification": classification
            },
        ).execute()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        Data.load()
        return {"FINISHED"}


class ChangeClassificationLevel(bpy.types.Operator):
    bl_idname = "bim.change_classification_level"
    bl_label = "Change Classification Level"
    parent_id: bpy.props.IntProperty()

    def execute(self, context):
        getReferences(self, context, parent_id=self.parent_id)
        return {"FINISHED"}
