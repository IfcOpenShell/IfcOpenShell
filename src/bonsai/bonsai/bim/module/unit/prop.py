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

import bpy
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.unit.data import UnitsData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def get_unit_classes(self, context):
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["unit_classes"]


def get_conversion_unit_types(self, context):
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["conversion_unit_types"]


def get_named_unit_types(self, context):
    if not UnitsData.is_loaded:
        UnitsData.load()
    return UnitsData.data["named_unit_types"]


class Unit(PropertyGroup):
    name: StringProperty(name="Name")
    unit_type: StringProperty(name="Unit Type")
    is_assigned: BoolProperty(name="Is Assigned")
    ifc_class: StringProperty(name="IFC Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMUnitProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    units: CollectionProperty(name="Units", type=Unit)
    active_unit_index: IntProperty(name="Active Unit Index")
    active_unit_id: IntProperty(name="Active Unit Id")
    unit_classes: EnumProperty(items=get_unit_classes, name="Unit Classes")
    conversion_unit_types: EnumProperty(items=get_conversion_unit_types, name="Conversion Unit Types")
    named_unit_types: EnumProperty(items=get_named_unit_types, name="Named Unit Types")
    unit_attributes: CollectionProperty(name="Unit Attributes", type=Attribute)
