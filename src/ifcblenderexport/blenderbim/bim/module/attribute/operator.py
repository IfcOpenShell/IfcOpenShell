import bpy
import json
import blenderbim.bim.module.attribute.edit_attributes as edit_attributes
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.attribute.data import Data


class EnableEditingAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_attributes"
    bl_label = "Enable Editing Attributes"
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.BIMAttributeProperties
        while len(props.attributes) > 0:
            props.attributes.remove(0)
        for attribute in Data.products[oprops.ifc_definition_id]:
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
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        props = obj.BIMAttributeProperties
        props.is_editing_attributes = False
        return {"FINISHED"}


class EditAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_attributes"
    bl_label = "Edit Attributes"
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.BIMAttributeProperties
        attributes = {}
        for attribute in Data.products[oprops.ifc_definition_id]:
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
        edit_attributes.Usecase(self.file, {
            "product": self.file.by_id(oprops.ifc_definition_id),
            "attributes": attributes
        }).execute()
        Data.load(oprops.ifc_definition_id)
        bpy.ops.bim.disable_editing_attributes(obj=self.obj, obj_type=self.obj_type)
        return {"FINISHED"}
