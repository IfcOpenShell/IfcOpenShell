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
import ifcopenshell.util.unit
import ifcopenshell.util.pset
import ifcopenshell.util.attribute
import blenderbim.bim.schema
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data
from ifcopenshell.api.cost.data import Data as CostData
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator


def get_pset_props(context, obj, obj_type):
    if obj_type == "Object":
        obj = bpy.data.objects.get(obj)
        return obj.PsetProperties
    elif obj_type == "Material":
        obj = bpy.data.materials.get(obj)
        return obj.PsetProperties
    elif obj_type == "Task":
        return context.scene.TaskPsetProperties
    elif obj_type == "Resource":
        return context.scene.ResourcePsetProperties
    elif obj_type == "Profile":
        return context.scene.ProfilePsetProperties
    elif obj_type == "WorkSchedule":
        return context.scene.WorkSchedulePsetProperties


def get_pset_obj_ifc_definition_id(context, obj, obj_type):
    if obj_type == "Object":
        obj = bpy.data.objects.get(obj)
        return obj.BIMObjectProperties.ifc_definition_id
    elif obj_type == "Material":
        obj = bpy.data.materials.get(obj)
        return obj.BIMObjectProperties.ifc_definition_id
    elif obj_type == "Task":
        return context.scene.BIMTaskTreeProperties.tasks[
            context.scene.BIMWorkScheduleProperties.active_task_index
        ].ifc_definition_id
    elif obj_type == "Resource":
        return context.scene.BIMResourceTreeProperties.resources[
            context.scene.BIMResourceProperties.active_resource_index
        ].ifc_definition_id
    elif obj_type == "Profile":
        return context.scene.BIMProfileProperties.profiles[
            context.scene.BIMProfileProperties.active_profile_index
        ].ifc_definition_id
    elif obj_type == "WorkSchedule":
        return context.scene.BIMWorkScheduleProperties.active_work_schedule_id


class TogglePsetExpansion(bpy.types.Operator):
    bl_idname = "bim.toggle_pset_expansion"
    bl_label = "Toggle Pset Expansion"
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        data = Data.psets if self.pset_id in Data.psets else Data.qtos
        data[self.pset_id]["is_expanded"] = not data[self.pset_id]["is_expanded"]
        return {"FINISHED"}


class EnablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.enable_pset_editing"
    bl_label = "Enable Pset Editing"
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.props = get_pset_props(context, self.obj, self.obj_type)

        self.props.properties.clear()

        data = Data.psets if self.pset_id in Data.psets else Data.qtos
        pset_data = data[self.pset_id]
        self.props.active_pset_name = pset_data["Name"]

        pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(pset_data["Name"])

        if pset_template:
            self.load_from_pset_template(pset_template, pset_data)
        else:
            self.load_from_pset_data(pset_data)

        self.props.active_pset_id = self.pset_id
        return {"FINISHED"}

    def load_from_pset_template(self, pset_template, pset_data):
        data = {Data.properties[p]["Name"]: Data.properties[p]["NominalValue"] for p in pset_data["Properties"]}
        for prop_template in pset_template.HasPropertyTemplates:
            if not prop_template.is_a("IfcSimplePropertyTemplate"):
                continue  # Other types not yet supported

            if prop_template.TemplateType == "P_SINGLEVALUE":
                try:
                    data_type = ifcopenshell.util.attribute.get_primitive_type(
                        IfcStore.get_schema().declaration_by_name(prop_template.PrimaryMeasureType or "IfcLabel")
                    )
                except:
                    # TODO: Occurs if the data type is something that exists in
                    # IFC4 and not in IFC2X3. To fully fix this we need to
                    # generate the IFC2X3 pset template definitions.
                    continue
            elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                data_type = "enum"
                enum_items = [v.wrappedValue for v in prop_template.Enumerators.EnumerationValues]
            elif prop_template.TemplateType in ["Q_LENGTH", "Q_AREA", "Q_VOLUME", "Q_WEIGHT", "Q_TIME"]:
                data_type = "float"
            elif prop_template.TemplateType == "Q_COUNT":
                data_type = "integer"
            else:
                continue  # Other types not yet supported

            new = self.props.properties.add()
            new.name = prop_template.Name
            new.is_null = data.get(prop_template.Name, None) is None
            new.is_optional = True
            new.data_type = data_type

            if data_type == "string":
                new.string_value = "" if new.is_null else data[prop_template.Name]
            elif data_type == "integer":
                new.int_value = 0 if new.is_null else data[prop_template.Name]
            elif data_type == "float":
                new.float_value = 0.0 if new.is_null else data[prop_template.Name]
            elif data_type == "boolean":
                new.bool_value = False if new.is_null else data[prop_template.Name]
            elif data_type == "enum":
                new.enum_items = json.dumps(enum_items)
                if data.get(prop_template.Name):
                    new.enum_value = data[prop_template.Name]

    def load_from_pset_data(self, pset_data):
        for prop_id in pset_data["Properties"]:
            prop = Data.properties[prop_id]

            value = prop["NominalValue"]
            new = self.props.properties.add()
            new.set_value(value)
            new.name = prop["Name"]
            new.is_null = value is None
            new.is_optional = True
            new.set_value(new.get_value_default() if new.is_null else value)


class DisablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.disable_pset_editing"
    bl_label = "Disable Pset Editing"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        props = get_pset_props(context, self.obj, self.obj_type)
        props.active_pset_id = 0
        return {"FINISHED"}


class EditPset(bpy.types.Operator):
    bl_idname = "bim.edit_pset"
    bl_label = "Edit Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()
    pset_id: bpy.props.IntProperty()
    properties: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = get_pset_obj_ifc_definition_id(context, self.obj, self.obj_type)
        properties = {}

        pset_id = self.pset_id or props.active_pset_id
        if self.properties:
            properties = json.loads(self.properties)
        else:
            data = Data.psets if pset_id in Data.psets else Data.qtos
            for prop in props.properties:
                properties[prop.name] = prop.get_value()

        if pset_id in Data.psets:
            ifcopenshell.api.run(
                "pset.edit_pset",
                self.file,
                **{
                    "pset": self.file.by_id(pset_id),
                    "name": props.active_pset_name,
                    "properties": properties,
                    "pset_template": blenderbim.bim.schema.ifc.psetqto.get_by_name(props.active_pset_name),
                },
            )
        else:
            for key, value in properties.items():
                if isinstance(value, float):
                    properties[key] = round(value, 4)
            ifcopenshell.api.run(
                "pset.edit_qto",
                self.file,
                **{
                    "qto": self.file.by_id(pset_id),
                    "name": props.active_pset_name,
                    "properties": properties,
                },
            )
            CostData.purge()
        Data.load(IfcStore.get_file(), ifc_definition_id)
        bpy.ops.bim.disable_pset_editing(obj=self.obj, obj_type=self.obj_type)
        return {"FINISHED"}


class RemovePset(bpy.types.Operator):
    bl_idname = "bim.remove_pset"
    bl_label = "Remove Pset"
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = get_pset_obj_ifc_definition_id(context, self.obj, self.obj_type)
        ifcopenshell.api.run(
            "pset.remove_pset",
            self.file,
            **{
                "product": self.file.by_id(ifc_definition_id),
                "pset": self.file.by_id(self.pset_id),
            },
        )
        Data.load(IfcStore.get_file(), ifc_definition_id)
        return {"FINISHED"}


class AddPset(bpy.types.Operator):
    bl_idname = "bim.add_pset"
    bl_label = "Add Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = get_pset_obj_ifc_definition_id(context, self.obj, self.obj_type)

        ifcopenshell.api.run(
            "pset.add_pset",
            self.file,
            **{
                "product": self.file.by_id(ifc_definition_id),
                "name": props.pset_name,
            },
        )
        Data.load(IfcStore.get_file(), ifc_definition_id)
        return {"FINISHED"}


class AddQto(bpy.types.Operator):
    bl_idname = "bim.add_qto"
    bl_label = "Add Qto"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = get_pset_obj_ifc_definition_id(context, self.obj, self.obj_type)
        ifcopenshell.api.run(
            "pset.add_qto",
            self.file,
            **{
                "product": self.file.by_id(ifc_definition_id),
                "name": props.qto_name,
            },
        )
        Data.load(IfcStore.get_file(), ifc_definition_id)
        return {"FINISHED"}


class GuessQuantity(bpy.types.Operator):
    bl_idname = "bim.guess_quantity"
    bl_label = "Guess Quantity"
    bl_options = {"REGISTER", "UNDO"}
    prop: bpy.props.StringProperty()

    def execute(self, context):
        self.qto_calculator = QtoCalculator()
        obj = context.active_object
        prop = obj.PsetProperties.properties.get(self.prop)
        prop.float_value = self.guess_quantity(obj, context)
        return {"FINISHED"}

    def guess_quantity(self, obj, context):
        quantity = self.qto_calculator.guess_quantity(self.prop, [p.name for p in obj.PsetProperties.properties], obj)
        if "area" in self.prop.lower():
            if context.scene.BIMProperties.area_unit:
                prefix, name = self.get_prefix_name(context.scene.BIMProperties.area_unit)
                quantity = ifcopenshell.util.unit.convert(quantity, None, "SQUARE_METRE", prefix, name)
        elif "volume" in self.prop.lower():
            if context.scene.BIMProperties.volume_unit:
                prefix, name = self.get_prefix_name(context.scene.BIMProperties.volume_unit)
                quantity = ifcopenshell.util.unit.convert(quantity, None, "CUBIC_METRE", prefix, name)
        else:
            prefix, name = self.get_blender_prefix_name(context)
            quantity = ifcopenshell.util.unit.convert(quantity, None, "METRE", prefix, name)
        return round(quantity, 3)

    def get_prefix_name(self, value):
        if "/" in value:
            return value.split("/")
        return None, value

    def get_blender_prefix_name(self, context):
        unit_settings = context.scene.unit_settings
        if unit_settings.system == "IMPERIAL":
            if unit_settings.length_unit == "INCHES":
                return None, "inch"
            elif unit_settings.length_unit == "FEET":
                return None, "foot"
        elif unit_settings.system == "METRIC":
            if unit_settings.length_unit == "METERS":
                return None, "METRE"
            return unit_settings.length_unit[0 : -len("METERS")], "METRE"
