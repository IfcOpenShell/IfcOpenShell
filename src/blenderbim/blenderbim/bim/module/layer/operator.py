import bpy
import json
import ifcopenshell.util.attribute
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.layer.data import Data


class LoadLayers(bpy.types.Operator):
    bl_idname = "bim.load_layers"
    bl_label = "Load Layers"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMLayerProperties
        while len(props.layers) > 0:
            props.layers.remove(0)
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

    def execute(self, context):
        context.scene.BIMLayerProperties.is_editing = False
        return {"FINISHED"}


class EnableEditingLayer(bpy.types.Operator):
    bl_idname = "bim.enable_editing_layer"
    bl_label = "Enable Editing Layer"
    layer: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMLayerProperties
        while len(props.layer_attributes) > 0:
            props.layer_attributes.remove(0)

        data = Data.layers[self.layer]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcPresentationLayerAssignment").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity" or data_type == "select":
                continue
            new = props.layer_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.string_value = "" if new.is_null else data[attribute.name()]
        props.active_layer_id = self.layer
        return {"FINISHED"}


class DisableEditingLayer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_layer"
    bl_label = "Disable Editing Layer"

    def execute(self, context):
        context.scene.BIMLayerProperties.active_layer_id = 0
        return {"FINISHED"}


class AddPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.add_presentation_layer"
    bl_label = "Add Layer"

    def execute(self, context):
        result = ifcopenshell.api.run("layer.add_layer", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_layers()
        bpy.ops.bim.enable_editing_layer(layer=result.id())
        return {"FINISHED"}


class EditPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.edit_presentation_layer"
    bl_label = "Edit Layer"

    def execute(self, context):
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
    layer: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMLayerProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("layer.remove_layer", self.file, **{"layer": self.file.by_id(self.layer)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_layers()
        return {"FINISHED"}


class AssignPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.assign_presentation_layer"
    bl_label = "Assign Presentation Layer"
    item: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
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
    item: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
        item = bpy.data.meshes.get(self.item) if self.item else context.active_object.data
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "layer.unassign_layer",
            self.file,
            **{"item": self.file.by_id(item.BIMMeshProperties.ifc_definition_id), "layer": self.file.by_id(self.layer)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
