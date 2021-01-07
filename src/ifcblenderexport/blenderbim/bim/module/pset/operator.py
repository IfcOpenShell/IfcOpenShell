import bpy
import json
import blenderbim.bim.module.pset.add_pset as add_pset
import blenderbim.bim.module.pset.edit_pset as edit_pset
import blenderbim.bim.module.pset.remove_pset as remove_pset
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.pset.data import Data


class TogglePsetExpansion(bpy.types.Operator):
    bl_idname = "bim.toggle_pset_expansion"
    bl_label = "Toggle Pset Expansion"
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        Data.psets[self.pset_id]["is_expanded"] = not Data.psets[self.pset_id]["is_expanded"]
        return {"FINISHED"}


class EnablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.enable_pset_editing"
    bl_label = "Enable Pset Editing"
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties

        while len(props.properties) > 0:
            props.properties.remove(0)

        props.active_pset_name = Data.psets[self.pset_id]["Name"]
        for prop in Data.psets[self.pset_id]["Properties"]:
            new = props.properties.add()
            new.name = prop["Name"]
            new.is_null = prop["is_null"]
            if prop["type"] == "string":
                new.string_value = prop["value"] or ""
            elif prop["type"] == "integer":
                new.int_value = prop["value"] or 0
            elif prop["type"] == "float":
                new.float_value = prop["value"] or 0.
            elif prop["type"] == "boolean":
                new.bool_value = prop["value"] or False
            elif prop["type"] == "enum":
                new.enum_items = json.dumps(prop["enum_items"])
                if prop["value"]:
                    new.enum_value = prop["value"]

        props.active_pset_id = self.pset_id
        return {"FINISHED"}


class DisablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.disable_pset_editing"
    bl_label = "Disable Pset Editing"

    def execute(self, context):
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        props.active_pset_id = 0
        return {"FINISHED"}


class EditPset(bpy.types.Operator):
    bl_idname = "bim.edit_pset"
    bl_label = "Edit Pset"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        properties = {}
        for prop in Data.psets[props.active_pset_id]["Properties"]:
            blender_prop = props.properties.get(prop["Name"])
            if not blender_prop:
                continue
            if blender_prop.is_null:
                properties[prop["Name"]] = None
            elif prop["type"] == "string":
                properties[prop["Name"]] = blender_prop.string_value
            elif prop["type"] == "boolean":
                properties[prop["Name"]] = blender_prop.bool_value
            elif prop["type"] == "integer":
                properties[prop["Name"]] = blender_prop.int_value
            elif prop["type"] == "float":
                properties[prop["Name"]] = blender_prop.float_value
            elif prop["type"] == "enum":
                properties[prop["Name"]] = blender_prop.enum_value
        edit_pset.Usecase(self.file, {
            "pset": self.file.by_id(props.active_pset_id),
            "Name": props.active_pset_name,
            "Properties": properties
        }).execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_pset_editing()
        return {"FINISHED"}


class RemovePset(bpy.types.Operator):
    bl_idname = "bim.remove_pset"
    bl_label = "Remove Pset"
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        remove_pset.Usecase(self.file, {
            "product": self.file.by_id(props.ifc_definition_id),
            "pset": self.file.by_id(self.pset_id),
        }).execute()
        Data.load(props.ifc_definition_id)
        return {"FINISHED"}


class AddPset(bpy.types.Operator):
    bl_idname = "bim.add_pset"
    bl_label = "Add Pset"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        add_pset.Usecase(self.file, {
            "product": self.file.by_id(props.ifc_definition_id),
            "Name": props.pset_name,
        }).execute()
        Data.load(props.ifc_definition_id)
        return {"FINISHED"}
