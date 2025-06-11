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

import bpy
from bpy.types import PropertyGroup
from bonsai.bim.prop import ObjProperty
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
import bonsai.tool as tool
from typing import TYPE_CHECKING, Union


def space_filter(self: "BIMObjectBoundaryProperties", object: bpy.types.Object) -> bool:
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcSpace") or entity.is_a("IfcExternalSpatialElement")
    return False


def boundary_filter(self: "BIMObjectBoundaryProperties", object: bpy.types.Object) -> bool:
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcRelSpaceBoundary")
    return False


def element_filter(self: "BIMObjectBoundaryProperties", object: bpy.types.Object) -> bool:
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcElement")
    return False


class BIMObjectBoundaryProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    relating_space: PointerProperty(name="RelatingSpace", type=bpy.types.Object, poll=space_filter)
    related_building_element: PointerProperty(name="RelatedBuildingElement", type=bpy.types.Object, poll=element_filter)
    parent_boundary: PointerProperty(name="ParentBoundary", type=bpy.types.Object, poll=boundary_filter)
    corresponding_boundary: PointerProperty(name="CorrespondingBoundary", type=bpy.types.Object, poll=boundary_filter)

    if TYPE_CHECKING:
        is_editing: bool
        relating_space: Union[bpy.types.Object, None]
        related_building_element: Union[bpy.types.Object, None]
        parent_boundary: Union[bpy.types.Object, None]
        corresponding_boundary: Union[bpy.types.Object, None]


class BIMBoundaryProperties(PropertyGroup):
    boundaries: bpy.props.CollectionProperty(type=ObjProperty, description="Decorated boundaries")

    if TYPE_CHECKING:
        boundaries: bpy.types.bpy_prop_collection_idprop[ObjProperty]
