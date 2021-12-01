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
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.attribute
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty, Attribute
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


unitclasses_enum = []
namedunittypes_enum = []


def purge():
    global unitclasses_enum
    global namedunittypes_enum
    unitclasses_enum = []
    namedunittypes_enum = []


def getUnitClasses(self, context):
    global unitclasses_enum
    if not len(unitclasses_enum) and IfcStore.get_file():
        declarations = ifcopenshell.util.schema.get_subtypes(IfcStore.get_schema().declaration_by_name("IfcNamedUnit"))
        unitclasses_enum.extend([(c, c, "") for c in sorted([d.name() for d in declarations])])
        unitclasses_enum.extend([("IfcDerivedUnit", "IfcDerivedUnit", ""), ("IfcMonetaryUnit", "IfcMonetaryUnit", "")])
    return unitclasses_enum


def getNamedUnitTypes(self, context):
    global namedunittypes_enum
    if not len(namedunittypes_enum) and IfcStore.get_file():
        values = ifcopenshell.util.attribute.get_enum_items(
            IfcStore.get_schema().declaration_by_name("IfcNamedUnit").all_attributes()[1]
        )
        namedunittypes_enum.extend([(c, c, "") for c in sorted(values)])
    return namedunittypes_enum


class Unit(PropertyGroup):
    name: StringProperty(name="Name")
    unit_type: StringProperty(name="Unit Type")
    is_assigned: BoolProperty(name="Is Assigned")
    icon: StringProperty(name="Icon")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMUnitProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    units: CollectionProperty(name="Units", type=Unit)
    active_unit_index: IntProperty(name="Active Unit Index")
    active_unit_id: IntProperty(name="Active Unit Id")
    unit_classes: EnumProperty(items=getUnitClasses, name="Unit Classes")
    named_unit_types: EnumProperty(items=getNamedUnitTypes, name="Named Unit Types")
    unit_attributes: CollectionProperty(name="Unit Attributes", type=Attribute)
