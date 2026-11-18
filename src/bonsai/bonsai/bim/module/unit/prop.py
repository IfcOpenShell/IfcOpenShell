# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from typing import TYPE_CHECKING

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

import bonsai.tool as tool
from bonsai.bim.module.unit.data import UnitsData
from bonsai.bim.prop import Attribute


def get_unit_classes(self: "BIMUnitProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["unit_classes"]


def get_conversion_unit_types(self: "BIMUnitProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["conversion_unit_types"]


def get_derived_unit_types(self: "BIMUnitProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["derived_unit_types"]


# Named unit types a derived unit can be built from (see tool.Unit.DERIVED_UNIT_COMPOSITIONS),
# with the label of their picker. Each gets a `derived_<type>` EnumProperty below.
DERIVED_COMPONENT_LABELS = {
    "LENGTHUNIT": "Length",
    "AREAUNIT": "Area",
    "VOLUMEUNIT": "Volume",
    "MASSUNIT": "Mass",
    "TIMEUNIT": "Time",
    "FORCEUNIT": "Force",
    "PRESSUREUNIT": "Pressure",
    "ENERGYUNIT": "Energy",
    "POWERUNIT": "Power",
    "PLANEANGLEUNIT": "Angle",
    "THERMODYNAMICTEMPERATUREUNIT": "Temperature",
    "AMOUNTOFSUBSTANCEUNIT": "Amount of Substance",
    "LUMINOUSINTENSITYUNIT": "Luminous Intensity",
    "LUMINOUSFLUXUNIT": "Luminous Flux",
}


def derived_component_property(unit_type: str) -> EnumProperty:
    def get_items(self: "BIMUnitProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
        from bonsai.bim.prop import cache_string

        if not tool.Ifc.get():
            return [("0", "Default", "")]
        return [
            (cache_string(i), cache_string(label), cache_string(description))
            for i, label, description in tool.Unit.get_component_unit_choices(unit_type)
        ]

    label = DERIVED_COMPONENT_LABELS[unit_type]
    return EnumProperty(
        items=get_items,
        name=label,
        description=f"{label} unit to build the derived unit from. Entries marked + are added to the file",
    )


def get_named_unit_types(self: "BIMUnitProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["named_unit_types"]


class Unit(PropertyGroup):
    unit_type: StringProperty(name="Unit Type")
    is_assigned: BoolProperty(name="Is Assigned")
    ifc_class: StringProperty(name="IFC Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        unit_type: str
        is_assigned: bool
        ifc_class: str
        ifc_definition_id: int


class BIMUnitProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    units: CollectionProperty(name="Units", type=Unit)
    active_unit_index: IntProperty(name="Active Unit Index")
    active_unit_id: IntProperty(name="Active Unit Id")
    unit_classes: EnumProperty(items=get_unit_classes, name="Unit Classes")
    conversion_unit_types: EnumProperty(items=get_conversion_unit_types, name="Conversion Unit Types")
    named_unit_types: EnumProperty(items=get_named_unit_types, name="Named Unit Types")
    derived_unit_types: EnumProperty(items=get_derived_unit_types, name="Derived Unit Types")
    derived_lengthunit: derived_component_property("LENGTHUNIT")
    derived_areaunit: derived_component_property("AREAUNIT")
    derived_volumeunit: derived_component_property("VOLUMEUNIT")
    derived_massunit: derived_component_property("MASSUNIT")
    derived_timeunit: derived_component_property("TIMEUNIT")
    derived_forceunit: derived_component_property("FORCEUNIT")
    derived_pressureunit: derived_component_property("PRESSUREUNIT")
    derived_energyunit: derived_component_property("ENERGYUNIT")
    derived_powerunit: derived_component_property("POWERUNIT")
    derived_planeangleunit: derived_component_property("PLANEANGLEUNIT")
    derived_thermodynamictemperatureunit: derived_component_property("THERMODYNAMICTEMPERATUREUNIT")
    derived_amountofsubstanceunit: derived_component_property("AMOUNTOFSUBSTANCEUNIT")
    derived_luminousintensityunit: derived_component_property("LUMINOUSINTENSITYUNIT")
    derived_luminousfluxunit: derived_component_property("LUMINOUSFLUXUNIT")
    unit_attributes: CollectionProperty(name="Unit Attributes", type=Attribute)

    if TYPE_CHECKING:
        is_editing: bool
        units: bpy.types.bpy_prop_collection_idprop[Unit]
        active_unit_index: int
        active_unit_id: int
        unit_classes: str
        conversion_unit_types: str
        named_unit_types: str
        derived_unit_types: str
        derived_lengthunit: str
        derived_areaunit: str
        derived_volumeunit: str
        derived_massunit: str
        derived_timeunit: str
        derived_forceunit: str
        derived_pressureunit: str
        derived_energyunit: str
        derived_powerunit: str
        derived_planeangleunit: str
        derived_thermodynamictemperatureunit: str
        derived_amountofsubstanceunit: str
        derived_luminousintensityunit: str
        derived_luminousfluxunit: str
        unit_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
