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
import blenderbim.tool as tool


def space_filter(self, object):
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcSpace") or entity.is_a("IfcExternalSpatialElement")
    return False


def boundary_filter(self, object):
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcRelSpaceBoundary")
    return False


def element_filter(self, object):
    entity = tool.Ifc.get_entity(object)
    if entity:
        return entity.is_a("IfcElement")
    return False


class BIMBoundaryProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    relating_space: PointerProperty(name="RelatingSpace", type=bpy.types.Object, poll=space_filter)
    related_building_element: PointerProperty(name="RelatedBuildingElement", type=bpy.types.Object, poll=element_filter)
    parent_boundary: PointerProperty(name="ParentBoundary", type=bpy.types.Object, poll=boundary_filter)
    corresponding_boundary: PointerProperty(name="CorrespondingBoundary", type=bpy.types.Object, poll=boundary_filter)
