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
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, CollectionProperty, EnumProperty
from typing import Union, TYPE_CHECKING, Literal, get_args

OperatorType = Literal["DIFFERENCE", "INTERSECTION", "UNION"]


class Boolean(PropertyGroup):
    name: StringProperty(name="Name")
    operator: EnumProperty(
        items=[(i, i, "") for i in get_args(OperatorType)],
        name="Operator",
        default="DIFFERENCE",
    )
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    level: IntProperty(name="Level")

    if TYPE_CHECKING:
        operator: OperatorType
        name: str
        ifc_definition_id: int
        level: int


class VoidProperties(PropertyGroup):
    desired_opening: PointerProperty(name="Desired Opening To Fill", type=bpy.types.Object)

    if TYPE_CHECKING:
        desired_opening: Union[bpy.types.Object, None]


class BIMBooleanProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    booleans: CollectionProperty(name="Booleans", type=Boolean)
    active_boolean_index: IntProperty(name="Active Boolean Index")
    operator: EnumProperty(
        items=[(i, i, "") for i in get_args(OperatorType)],
        name="Operator",
        default="DIFFERENCE",
    )

    if TYPE_CHECKING:
        is_editing: bool
        booleans: bpy.types.bpy_prop_collection_idprop[Boolean]
        active_boolean_index: int
        operator: OperatorType

    @property
    def active_boolean(self) -> Union[Boolean, None]:
        if self.booleans and 0 <= self.active_boolean_index < len(self.booleans):
            return self.booleans[self.active_boolean_index]
