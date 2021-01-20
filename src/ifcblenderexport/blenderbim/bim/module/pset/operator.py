import bpy
import json
import ifcopenshell.util.unit
import blenderbim.bim.module.pset.add_pset as add_pset
import blenderbim.bim.module.pset.edit_pset as edit_pset
import blenderbim.bim.module.pset.remove_pset as remove_pset
import blenderbim.bim.module.pset.add_qto as add_qto
import blenderbim.bim.module.pset.edit_qto as edit_qto
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.pset.data import Data
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator


class TogglePsetExpansion(bpy.types.Operator):
    bl_idname = "bim.toggle_pset_expansion"
    bl_label = "Toggle Pset Expansion"
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.context.active_object
        data = Data.psets if self.pset_id in Data.psets else Data.qtos
        data[self.pset_id]["is_expanded"] = not data[self.pset_id]["is_expanded"]
        return {"FINISHED"}


class EnablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.enable_pset_editing"
    bl_label = "Enable Pset Editing"
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        props = obj.PsetProperties

        while len(props.properties) > 0:
            props.properties.remove(0)

        data = Data.psets if self.pset_id in Data.psets else Data.qtos
        props.active_pset_name = data[self.pset_id]["Name"]
        for prop in data[self.pset_id]["Properties"]:
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
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        props = obj.PsetProperties
        props.active_pset_id = 0
        return {"FINISHED"}


class EditPset(bpy.types.Operator):
    bl_idname = "bim.edit_pset"
    bl_label = "Edit Pset"
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.PsetProperties
        properties = {}
        data = Data.psets if props.active_pset_id in Data.psets else Data.qtos
        for prop in data[props.active_pset_id]["Properties"]:
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
        if props.active_pset_id in Data.psets:
            edit_pset.Usecase(self.file, {
                "pset": self.file.by_id(props.active_pset_id),
                "Name": props.active_pset_name,
                "Properties": properties
            }).execute()
        else:
            edit_qto.Usecase(self.file, {
                "qto": self.file.by_id(props.active_pset_id),
                "Name": props.active_pset_name,
                "Properties": properties
            }).execute()
        Data.load(oprops.ifc_definition_id)
        bpy.ops.bim.disable_pset_editing(obj=self.obj, obj_type=self.obj_type)
        return {"FINISHED"}


class RemovePset(bpy.types.Operator):
    bl_idname = "bim.remove_pset"
    bl_label = "Remove Pset"
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
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
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.PsetProperties
        add_pset.Usecase(self.file, {
            "product": self.file.by_id(oprops.ifc_definition_id),
            "Name": props.pset_name if self.obj_type == "Object" else props.material_pset_name,
        }).execute()
        Data.load(oprops.ifc_definition_id)
        return {"FINISHED"}


class AddQto(bpy.types.Operator):
    bl_idname = "bim.add_qto"
    bl_label = "Add Qto"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.PsetProperties
        add_qto.Usecase(self.file, {
            "product": self.file.by_id(oprops.ifc_definition_id),
            "Name": props.qto_name,
        }).execute()
        Data.load(oprops.ifc_definition_id)
        return {"FINISHED"}


class GuessQuantity(bpy.types.Operator):
    bl_idname = "bim.guess_quantity"
    bl_label = "Guess Quantity"
    prop: bpy.props.StringProperty()

    def execute(self, context):
        self.qto_calculator = QtoCalculator()
        obj = bpy.context.active_object
        prop = obj.PsetProperties.properties.get(self.prop)
        prop.float_value = self.guess_quantity(obj)
        return {"FINISHED"}

    def guess_quantity(self, obj):
        quantity = self.qto_calculator.guess_quantity(self.prop, [p.name for p in obj.PsetProperties.properties], obj)
        if "area" in self.prop.lower():
            if bpy.context.scene.BIMProperties.area_unit:
                prefix, name = self.get_prefix_name(bpy.context.scene.BIMProperties.area_unit)
                quantity = ifcopenshell.util.unit.convert(quantity, None, "SQUARE_METRE", prefix, name)
        elif "volume" in self.prop.lower():
            if bpy.context.scene.BIMProperties.volume_unit:
                prefix, name = self.get_prefix_name(bpy.context.scene.BIMProperties.volume_unit)
                quantity = ifcopenshell.util.unit.convert(quantity, None, "CUBIC_METRE", prefix, name)
        else:
            prefix, name = self.get_blender_prefix_name()
            quantity = ifcopenshell.util.unit.convert(quantity, None, "METRE", prefix, name)
        return round(quantity, 3)

    def get_prefix_name(self, value):
        if "/" in value:
            return value.split("/")
        return None, value

    def get_blender_prefix_name(self):
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            if bpy.context.scene.unit_settings.length_unit == "INCHES":
                return None, "inch"
            elif bpy.context.scene.unit_settings.length_unit == "FEET":
                return None, "foot"
        elif bpy.context.scene.unit_settings.system == "METRIC":
            if bpy.context.scene.unit_settings.length_unit == "METERS":
                return None, "METRE"
            return bpy.context.scene.unit_settings.length_unit[0 : -len("METERS")], "METRE"
