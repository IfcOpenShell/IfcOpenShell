
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
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.classification.data import Data
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
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMClassificationProperties
        ifcopenshell.api.run(
            "classification.add_classification",
            IfcStore.get_file(),
            **{"classification": Data.library_file.by_id(int(props.available_classifications))},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification"
    bl_label = "Enable Editing Classification"
    bl_options = {"REGISTER", "UNDO"}
    classification: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        props.classification_attributes.clear()
        classification_data = Data.classifications[self.classification]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcClassification").all_attributes():
            new = props.classification_attributes.add()
            new.name = attribute.name()
            new.is_null = classification_data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = "string"
            if attribute.name() == "ReferenceTokens":
                new.string_value = "" if new.is_null else json.dumps(classification_data[attribute.name()])
            else:
                new.string_value = "" if new.is_null else classification_data[attribute.name()]
        props.active_classification_id = self.classification
        return {"FINISHED"}


class DisableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification"
    bl_label = "Disable Editing Classification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMClassificationProperties.active_classification_id = 0
        return {"FINISHED"}


class RemoveClassification(bpy.types.Operator):
    bl_idname = "bim.remove_classification"
    bl_label = "Remove Classification"
    bl_options = {"REGISTER", "UNDO"}
    classification: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.remove_classification",
            self.file,
            **{"classification": self.file.by_id(self.classification)},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditClassification(bpy.types.Operator):
    bl_idname = "bim.edit_classification"
    bl_label = "Edit Classification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
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
        ifcopenshell.api.run(
            "classification.edit_classification",
            self.file,
            **{"classification": self.file.by_id(props.active_classification_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_classification()
        return {"FINISHED"}


class EnableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification_reference"
    bl_label = "Enable Editing Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMClassificationReferenceProperties
        props.reference_attributes.clear()
        reference_data = Data.references[self.reference]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcClassificationReference").all_attributes():
            if attribute.name() == "ReferencedSource":
                continue
            new = props.reference_attributes.add()
            new.name = attribute.name()
            new.is_null = reference_data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = "string"
            new.string_value = "" if new.is_null else reference_data[attribute.name()]
        props.active_reference_id = self.reference
        return {"FINISHED"}


class DisableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification_reference"
    bl_label = "Disable Editing Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        obj.BIMClassificationReferenceProperties.active_reference_id = 0
        return {"FINISHED"}


class RemoveClassificationReference(bpy.types.Operator):
    bl_idname = "bim.remove_classification_reference"
    bl_label = "Remove Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.remove_reference",
            self.file,
            **{
                "reference": self.file.by_id(self.reference),
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
            },
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditClassificationReference(bpy.types.Operator):
    bl_idname = "bim.edit_classification_reference"
    bl_label = "Edit Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMClassificationReferenceProperties
        attributes = {}
        for attribute in props.reference_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.edit_reference",
            self.file,
            **{"reference": self.file.by_id(props.active_reference_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_classification_reference()
        return {"FINISHED"}


class AddClassificationReference(bpy.types.Operator):
    bl_idname = "bim.add_classification_reference"
    bl_label = "Add Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()

        classification = None

        props = context.scene.BIMClassificationProperties
        classification_name = Data.library_classifications[int(props.available_classifications)]
        for classification_id, classification in Data.classifications.items():
            if classification["Name"] == classification_name:
                classification = self.file.by_id(classification_id)
                break

        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            **{
                "reference": Data.library_file.by_id(self.reference),
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "classification": classification,
            },
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class ChangeClassificationLevel(bpy.types.Operator):
    bl_idname = "bim.change_classification_level"
    bl_label = "Change Classification Level"
    bl_options = {"REGISTER", "UNDO"}
    parent_id: bpy.props.IntProperty()

    def execute(self, context):
        getReferences(self, context, parent_id=self.parent_id)
        return {"FINISHED"}
