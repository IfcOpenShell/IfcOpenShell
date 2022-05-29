# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool


class Unit(blenderbim.core.tool.Unit):
    @classmethod
    def clear_active_unit(cls):
        bpy.context.scene.BIMUnitProperties.active_unit_id = 0

    @classmethod
    def disable_editing_units(cls):
        bpy.context.scene.BIMUnitProperties.is_editing = False

    @classmethod
    def enable_editing_units(cls):
        bpy.context.scene.BIMUnitProperties.is_editing = True

    @classmethod
    def export_unit_attributes(cls):
        def callback(attributes, prop):
            if prop.name == "Dimensions":
                try:
                    attributes[prop.name] = json.loads(prop.get_value())
                except:
                    attributes[prop.name] = (0, 0, 0, 0, 0, 0, 0)
                return True

        props = bpy.context.scene.BIMUnitProperties
        return blenderbim.bim.helper.export_attributes(props.unit_attributes, callback=callback)

    @classmethod
    def get_scene_unit_name(cls, unit_type):
        props = bpy.context.scene.unit_settings
        is_metric = props.system == "METRIC" or props.system == "NONE"

        if is_metric:
            name = "METRE"
        elif props.length_unit == "MILES":
            name = "mile"
        elif props.length_unit == "FEET" or props.length_unit == "ADAPTIVE":
            name = "foot"
        elif props.length_unit == "INCHES":
            name = "inch"
        elif props.length_unit == "THOU":
            name = "thou"

        if unit_type == "length":
            return name
        elif unit_type == "area":
            if is_metric:
                return f"SQUARE_{name}"
            return f"square {name}"
        elif unit_type == "volume":
            if is_metric:
                return f"CUBIC_{name}"
            return f"cubic {name}"

    @classmethod
    def get_scene_unit_si_prefix(cls):
        props = bpy.context.scene.unit_settings
        if props.length_unit == "ADAPTIVE" or props.length_unit == "METERS":
            return
        return props.length_unit.replace("METERS", "")

    @classmethod
    def get_si_name_from_unit_type(cls, unit_type):
        return ifcopenshell.util.unit.si_type_names.get(unit_type, None)

    @classmethod
    def import_unit_attributes(cls, unit):
        def callback(name, prop, data):
            if name == "Dimensions" and data["type"] != "IfcSIUnit":
                new = bpy.context.scene.BIMUnitProperties.unit_attributes.add()
                new.name = name
                new.is_null = data[name] is None
                new.is_optional = False
                new.data_type = "string"
                new.string_value = json.dumps([e for e in tool.Ifc.get().by_id(data["id"]).Dimensions])
                return True

        props = bpy.context.scene.BIMUnitProperties
        props.unit_attributes.clear()
        blenderbim.bim.helper.import_attributes2(unit, props.unit_attributes, callback=callback)

    @classmethod
    def import_units(cls):
        props = bpy.context.scene.BIMUnitProperties
        props.units.clear()

        units = []
        for unit_class in ["IfcDerivedUnit", "IfcMonetaryUnit", "IfcNamedUnit"]:
            units += tool.Ifc.get().by_type(unit_class)

        assigned_units = tool.Ifc.get().by_type("IfcUnitAssignment")
        if assigned_units:
            assigned_units = assigned_units[0].Units

        for unit in units:
            name = ""
            if unit.is_a("IfcMonetaryUnit"):
                name = unit.Currency
            elif not unit.is_a("IfcDerivedUnit"):
                name = unit.Name or ""

            if unit.is_a("IfcSIUnit") and unit.Prefix:
                if "_" in name:
                    name_components = name.split("_")
                    name = f"{name_components[0]} {unit.Prefix}{name_components[1]}"
                else:
                    name = f"{unit.Prefix}{name}"

            if unit.is_a("IfcMonetaryUnit"):
                unit_type = "CURRENCY"
            else:
                unit_type = getattr(unit, "UserDefinedType", None)
                if not unit_type:
                    unit_type = getattr(unit, "UnitType", None)

            new = props.units.add()
            new.ifc_definition_id = unit.id()
            new.name = name
            new.unit_type = unit_type
            new.is_assigned = unit in assigned_units
            new.ifc_class = unit.is_a()

    @classmethod
    def is_scene_unit_metric(cls):
        return bpy.context.scene.unit_settings.system in ["METRIC", "NONE"]

    @classmethod
    def is_unit_class(cls, unit, ifc_class):
        return unit.is_a(ifc_class)

    @classmethod
    def set_active_unit(cls, unit):
        bpy.context.scene.BIMUnitProperties.active_unit_id = unit.id()
