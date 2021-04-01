import bpy
import json
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.attribute.data import Data


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
                new.float_value = attribute["value"] or 0.0
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
        product = self.file.by_id(oprops.ifc_definition_id)
        ifcopenshell.api.run(
            "attribute.edit_attributes", self.file, **{"product": product, "attributes": attributes}
        )
        if "Name" in attributes:
            new_name = "{}/{}".format(product.is_a(), product.Name or "Unnamed")
            collection = bpy.data.collections.get(obj.name)
            if collection:
                collection.name = new_name
            obj.name = new_name
        Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        bpy.ops.bim.disable_editing_attributes(obj=obj.name, obj_type=self.obj_type)
        return {"FINISHED"}


class GenerateGlobalId(bpy.types.Operator):
    bl_idname = "bim.generate_global_id"
    bl_label = "Regenerate GlobalId"

    def execute(self, context):
        index = bpy.context.active_object.BIMAttributeProperties.attributes.find("GlobalId")
        if index >= 0:
            global_id = bpy.context.active_object.BIMAttributeProperties.attributes[index]
        else:
            global_id = bpy.context.active_object.BIMAttributeProperties.attributes.add()
        global_id.name = "GlobalId"
        global_id.data_type = "string"
        global_id.string_value = ifcopenshell.guid.new()
        return {"FINISHED"}
