import bpy
import json
import blenderbim.bim.module.attribute.edit_attributes as edit_attributes
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.attribute.data import Data


class EnableEditingAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_attributes"
    bl_label = "Enable Editing Attributes"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        while len(props.attributes) > 0:
            props.attributes.remove(0)
        for attribute in Data.products[props.ifc_definition_id]:
            new = props.attributes.add()
            if attribute["type"] == "entity":
                continue
            new.name = attribute["name"]
            new.is_null = attribute["is_null"]
            if attribute["type"] == "string" or attribute["type"] == "list":
                new.string_value = attribute["value"] or ""
            elif attribute["type"] == "integer":
                new.int_value = attribute["value"] or 0
            elif attribute["type"] == "float":
                new.float_value = attribute["value"] or 0.
            elif attribute["type"] == "enum":
                new.enum_items = json.dumps(attribute["enum_items"])
                if attribute["value"]:
                    new.enum_value = attribute["value"]
        props.is_editing_attributes = True
        return {"FINISHED"}


class DisableEditingAttributes(bpy.types.Operator):
    bl_idname = "bim.disable_editing_attributes"
    bl_label = "Disable Editing Attributes"

    def execute(self, context):
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        props.is_editing_attributes = False
        return {"FINISHED"}


class EditAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_attributes"
    bl_label = "Edit Attributes"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        attributes = {}
        for attribute in Data.products[props.ifc_definition_id]:
            blender_attribute = props.attributes.get(attribute["name"])
            if not blender_attribute:
                continue
            if attribute["is_optional"] and blender_attribute.is_null:
                attributes[attribute["name"]] = None
            elif attribute["type"] == "string":
                attributes[attribute["name"]] = blender_attribute.string_value
            elif attribute["type"] == "list":
                values = blender_attribute.string_value[1:-1].split(", ")
                if attribute["list_type"] == "float":
                    values = [float(v) for v in values]
                elif attribute["list_type"] == "integer":
                    values = [int(v) for v in values]
                attributes[attribute["name"]] = values
            elif attribute["type"] == "integer":
                attributes[attribute["name"]] = blender_attribute.int_value
            elif attribute["type"] == "float":
                attributes[attribute["name"]] = blender_attribute.float_value
            elif attribute["type"] == "enum":
                attributes[attribute["name"]] = blender_attribute.enum_value
        usecase = edit_attributes.Usecase(self.file, {
            "product": self.file.by_id(props.ifc_definition_id),
            "attributes": attributes
        })
        usecase.execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_attributes()
        return {"FINISHED"}
