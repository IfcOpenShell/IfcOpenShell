
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
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.unit.data import Data


class AssignUnit(bpy.types.Operator):
    bl_idname = "bim.assign_unit"
    bl_label = "Assign Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.unit:
            ifcopenshell.api.run("unit.assign_unit", self.file, units=[self.file.by_id(self.unit)])
        else:
            ifcopenshell.api.run("unit.assign_unit", self.file, **self.get_units(context))
        Data.load(self.file)
        if self.unit:
            bpy.ops.bim.load_units()
        return {"FINISHED"}

    def get_units(self, context):
        scene = context.scene
        units = {
            "length": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
            "area": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
            "volume": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
        }
        for data in units.values():
            if data["raw"] == "ADAPTIVE":
                if data["is_metric"]:
                    data["raw"] = "METERS"
                else:
                    data["raw"] = "FEET"
        return units


class UnassignUnit(bpy.types.Operator):
    bl_idname = "bim.unassign_unit"
    bl_label = "Unassign Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("unit.unassign_unit", IfcStore.get_file(), units=[self.file.by_id(self.unit)])
        Data.load(self.file)
        bpy.ops.bim.load_units()
        return {"FINISHED"}


class LoadUnits(bpy.types.Operator):
    bl_idname = "bim.load_units"
    bl_label = "Load Units"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMUnitProperties
        props.units.clear()

        for ifc_definition_id, unit in Data.units.items():
            name = unit.get("Name", "")

            if unit["type"] == "IfcMonetaryUnit":
                name = unit["Currency"]

            if unit["type"] == "IfcSIUnit" and unit["Prefix"]:
                if "_" in name:
                    name_components = name.split("_")
                    name = f"{name_components[0]} {unit['Prefix']}{name_components[1]}"
                else:
                    name = f"{unit['Prefix']}{name}"

            icon = "MOD_MESHDEFORM"
            if unit["type"] == "IfcSIUnit":
                icon = "SNAP_GRID"
            elif unit["type"] == "IfcMonetaryUnit":
                icon = "COPY_ID"

            unit_type = unit.get("UserDefinedType", None)
            if not unit_type:
                unit_type = unit.get("UnitType", None)
            if unit["type"] == "IfcMonetaryUnit":
                unit_type = "CURRENCY"

            new = props.units.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = name
            new.unit_type = unit_type
            new.is_assigned = ifc_definition_id in Data.unit_assignment
            new.icon = icon

        props.is_editing = True
        bpy.ops.bim.disable_editing_unit()
        return {"FINISHED"}


class DisableUnitEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_unit_editing_ui"
    bl_label = "Disable Unit Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMUnitProperties.is_editing = False
        return {"FINISHED"}


class RemoveUnit(bpy.types.Operator):
    bl_idname = "bim.remove_unit"
    bl_label = "Remove Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMUnitProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("unit.remove_unit", self.file, **{"unit": self.file.by_id(self.unit)})
        Data.load(self.file)
        bpy.ops.bim.load_units()
        return {"FINISHED"}


class AddMonetaryUnit(bpy.types.Operator):
    bl_idname = "bim.add_monetary_unit"
    bl_label = "Add Monetary Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMUnitProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("unit.add_monetary_unit", self.file)
        Data.load(self.file)
        bpy.ops.bim.load_units()
        return {"FINISHED"}


class AddSIUnit(bpy.types.Operator):
    bl_idname = "bim.add_si_unit"
    bl_label = "Add SI Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMUnitProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "unit.add_si_unit",
            self.file,
            unit_type=props.named_unit_types,
            name=ifcopenshell.util.unit.si_type_names[props.named_unit_types],
        )
        Data.load(self.file)
        bpy.ops.bim.load_units()
        return {"FINISHED"}


class AddContextDependentUnit(bpy.types.Operator):
    bl_idname = "bim.add_context_dependent_unit"
    bl_label = "Add Context Dependent Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMUnitProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "unit.add_context_dependent_unit", self.file, unit_type=props.named_unit_types, name="THINGAMAJIG"
        )
        Data.load(self.file)
        bpy.ops.bim.load_units()
        return {"FINISHED"}



class EnableEditingUnit(bpy.types.Operator):
    bl_idname = "bim.enable_editing_unit"
    bl_label = "Enable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMUnitProperties
        props.unit_attributes.clear()
        data = Data.units[self.unit]
        blenderbim.bim.helper.import_attributes(
            data["type"],
            props.unit_attributes, 
            data, 
            lambda name, prop, data: self.import_attributes(name, prop, data, context))
        props.active_unit_id = self.unit
        return {"FINISHED"}

    def import_attributes(self, name, prop, data, context):
        if name == "Dimensions" and data["type"] != "IfcSIUnit":
            new = context.scene.BIMUnitProperties.unit_attributes.add()
            new.name = name
            new.is_null = data[name] is None
            new.is_optional = False
            new.data_type = "string"
            new.string_value = json.dumps([e for e in IfcStore.get_file().by_id(data["id"]).Dimensions])
            return True


class DisableEditingUnit(bpy.types.Operator):
    bl_idname = "bim.disable_editing_unit"
    bl_label = "Disable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMUnitProperties.active_unit_id = 0
        return {"FINISHED"}


class EditUnit(bpy.types.Operator):
    bl_idname = "bim.edit_unit"
    bl_label = "Edit Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMUnitProperties
        attributes = blenderbim.bim.helper.export_attributes(props.unit_attributes, self.export_attributes)
        self.file = IfcStore.get_file()
        unit = self.file.by_id(props.active_unit_id)
        if unit.is_a("IfcMonetaryUnit"):
            ifcopenshell.api.run("unit.edit_monetary_unit", self.file, **{"unit": unit, "attributes": attributes})
        elif unit.is_a("IfcDerivedUnit"):
            ifcopenshell.api.run("unit.edit_derived_unit", self.file, **{"unit": unit, "attributes": attributes})
        elif unit.is_a("IfcNamedUnit"):
            ifcopenshell.api.run("unit.edit_named_unit", self.file, **{"unit": unit, "attributes": attributes})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_units()
        return {"FINISHED"}

    def export_attributes(self, attributes, prop):
        if prop.name == "Dimensions":
            try:
                attributes[prop.name] = json.loads(prop.get_value())
            except:
                attributes[prop.name] = (0, 0, 0, 0, 0, 0, 0)
            return True
