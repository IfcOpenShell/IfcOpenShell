# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
import bpy
import json
import math
import ifcopenshell
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import Union, Literal, Any, TYPE_CHECKING, assert_never

if TYPE_CHECKING:
    from bonsai.bim.module.unit.prop import BIMUnitProperties


class Unit(bonsai.core.tool.Unit):
    UNIT_TYPE = Literal["LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT"]

    @classmethod
    def get_unit_props(cls) -> BIMUnitProperties:
        return bpy.context.scene.BIMUnitProperties

    @classmethod
    def clear_active_unit(cls) -> None:
        props = cls.get_unit_props()
        props.active_unit_id = 0

    @classmethod
    def disable_editing_units(cls) -> None:
        props = cls.get_unit_props()
        props.is_editing = False

    @classmethod
    def enable_editing_units(cls) -> None:
        props = cls.get_unit_props()
        props.is_editing = True

    @classmethod
    def export_unit_attributes(cls) -> dict[str, Any]:
        def callback(attributes, prop):
            if prop.name == "Dimensions":
                try:
                    attributes[prop.name] = json.loads(prop.get_value())
                except:
                    attributes[prop.name] = (0, 0, 0, 0, 0, 0, 0)
                return True

        props = cls.get_unit_props()
        return bonsai.bim.helper.export_attributes(props.unit_attributes, callback=callback)

    @classmethod
    def get_scene_unit_name(cls, unit_type: UNIT_TYPE) -> str:
        bim_props = tool.Blender.get_bim_props()
        if unit_type == "LENGTHUNIT":
            props = bpy.context.scene.unit_settings
            if props.length_unit == "MILES":
                return "mile"
            elif props.length_unit == "FEET" or props.length_unit == "ADAPTIVE":
                return "foot"
            elif props.length_unit == "INCHES":
                return "inch"
            elif props.length_unit == "THOU":
                return "thou"
            return "foot"
        elif unit_type == "AREAUNIT":
            return bim_props.area_unit
        elif unit_type == "VOLUMEUNIT":
            return bim_props.volume_unit
        else:
            assert_never()

    @classmethod
    def get_scene_unit_si_prefix(cls, unit_type: UNIT_TYPE) -> Union[str, None]:
        bim_props = tool.Blender.get_bim_props()
        if unit_type == "LENGTHUNIT":
            props = bpy.context.scene.unit_settings
            if props.length_unit == "ADAPTIVE" or props.length_unit == "METERS":
                return
            return props.length_unit.replace("METERS", "")
        elif unit_type == "AREAUNIT":
            unit = bim_props.area_unit
        elif unit_type == "VOLUMEUNIT":
            unit = bim_props.volume_unit
        else:
            assert_never(unit_type)
        if "/" in unit:
            return unit.split("/")[0]

    @classmethod
    def import_unit_attributes(cls, unit: ifcopenshell.entity_instance) -> None:
        props = cls.get_unit_props()

        def callback(name, prop, data):
            if name == "Dimensions" and data["type"] != "IfcSIUnit":
                new = props.unit_attributes.add()
                new.name = name
                new.is_null = data[name] is None
                new.is_optional = False
                new.data_type = "string"
                new.string_value = json.dumps([e for e in tool.Ifc.get().by_id(data["id"]).Dimensions])
                return True

        props.unit_attributes.clear()
        bonsai.bim.helper.import_attributes2(unit, props.unit_attributes, callback=callback)

    @classmethod
    def import_units(cls) -> None:
        props = tool.Unit.get_unit_props()
        props.units.clear()

        units = []
        for unit_class in ["IfcDerivedUnit", "IfcMonetaryUnit", "IfcNamedUnit"]:
            units += tool.Ifc.get().by_type(unit_class)

        assigned_units = []
        if assignment := tool.Ifc.get().by_type("IfcProject")[0].UnitsInContext:
            assigned_units = assignment.Units

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
    def is_scene_unit_metric(cls) -> bool:
        return bpy.context.scene.unit_settings.system in ["METRIC", "NONE"]

    @classmethod
    def is_unit_class(cls, unit: ifcopenshell.entity_instance, ifc_class: str) -> bool:
        return unit.is_a(ifc_class)

    @classmethod
    def set_active_unit(cls, unit: ifcopenshell.entity_instance) -> None:
        props = cls.get_unit_props()
        props.active_unit_id = unit.id()

    @classmethod
    def get_project_currency_unit(cls) -> Union[ifcopenshell.entity_instance, None]:
        if assignment := tool.Ifc.get().by_type("IfcProject")[0].UnitsInContext:
            for unit in assignment.Units:
                if unit.is_a("IfcMonetaryUnit"):
                    return unit

    @classmethod
    def get_currency_name(cls) -> Union[str, None]:
        unit = cls.get_project_currency_unit()
        if unit:
            return unit.Currency

    @classmethod
    def blender_format_unit(cls, value: float) -> str:
        return bpy.utils.units.to_string(
            bpy.context.scene.unit_settings.system,
            "LENGTH",
            value,
            precision=4,
            split_unit=bpy.context.scene.unit_settings.system == "IMPERIAL",
        )

    @classmethod
    def format_value(cls, value: float) -> str:
        precision = tool.Ifc.get().by_type("IfcGeometricRepresentationContext")[0].Precision
        if precision:
            decimal_places = math.ceil(math.log10(1 / precision))
        else:
            precision = 1e-5
            decimal_places = 5
        return str(round(precision * round(value / precision), decimal_places))
