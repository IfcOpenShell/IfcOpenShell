
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
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.layer.data import Data


class LoadLayers(bpy.types.Operator):
    bl_idname = "bim.load_layers"
    bl_label = "Load Layers"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMLayerProperties
        props.layers.clear()
        for layer_id, layer in Data.layers.items():
            new = props.layers.add()
            new.name = layer["Name"] or "Unnamed"
            new.ifc_definition_id = layer_id
        props.is_editing = True
        bpy.ops.bim.disable_editing_layer()
        return {"FINISHED"}


class DisableLayerEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_layer_editing_ui"
    bl_label = "Disable Layer Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMLayerProperties.is_editing = False
        return {"FINISHED"}


class EnableEditingLayer(bpy.types.Operator):
    bl_idname = "bim.enable_editing_layer"
    bl_label = "Enable Editing Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMLayerProperties
        props.layer_attributes.clear()

        blenderbim.bim.helper.import_attributes(
            "IfcPresentationLayerAssignment", props.layer_attributes, Data.layers[self.layer]
        )

        props.active_layer_id = self.layer
        return {"FINISHED"}


class DisableEditingLayer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_layer"
    bl_label = "Disable Editing Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMLayerProperties.active_layer_id = 0
        return {"FINISHED"}


class AddPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.add_presentation_layer"
    bl_label = "Add Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("layer.add_layer", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_layers()
        bpy.ops.bim.enable_editing_layer(layer=result.id())
        return {"FINISHED"}


class EditPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.edit_presentation_layer"
    bl_label = "Edit Layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMLayerProperties
        attributes = {}
        for attribute in props.layer_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "layer.edit_layer", self.file, **{"layer": self.file.by_id(props.active_layer_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_layers()
        return {"FINISHED"}


class RemovePresentationLayer(bpy.types.Operator):
    bl_idname = "bim.remove_presentation_layer"
    bl_label = "Remove Presentation Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMLayerProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("layer.remove_layer", self.file, **{"layer": self.file.by_id(self.layer)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_layers()
        return {"FINISHED"}


class AssignPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.assign_presentation_layer"
    bl_label = "Assign Presentation Layer"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        item = bpy.data.meshes.get(self.item) if self.item else context.active_object.data
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "layer.assign_layer",
            self.file,
            **{"item": self.file.by_id(item.BIMMeshProperties.ifc_definition_id), "layer": self.file.by_id(self.layer)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.unassign_presentation_layer"
    bl_label = "Unassign Presentation Layer"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        item = bpy.data.meshes.get(self.item) if self.item else context.active_object.data
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "layer.unassign_layer",
            self.file,
            **{"item": self.file.by_id(item.BIMMeshProperties.ifc_definition_id), "layer": self.file.by_id(self.layer)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
