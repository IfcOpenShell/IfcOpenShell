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
from ifcopenshell.util.doc import get_entity_doc
import bonsai.tool as tool
from bonsai.bim.prop import Attribute
from bonsai.bim.module.constraint.data import ConstraintsData
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


def get_available_constraint_types(self, context):
    if not ConstraintsData.is_loaded:
        ConstraintsData.load()
    return ConstraintsData.data["constraint_types_enum"]


class Constraint(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMConstraintProperties(PropertyGroup):
    constraint_attributes: CollectionProperty(name="Constraint Attributes", type=Attribute)
    active_constraint_id: IntProperty(name="Active Constraint Id")
    constraints: CollectionProperty(name="Constraints", type=Constraint)
    active_constraint_index: IntProperty(name="Active Constraint Index")
    is_editing: StringProperty(name="Is Editing")


class BIMObjectConstraintProperties(PropertyGroup):
    is_adding: StringProperty(name="Is Adding")
    available_constraint_types: EnumProperty(items=get_available_constraint_types, name="Available Constraint Types")
