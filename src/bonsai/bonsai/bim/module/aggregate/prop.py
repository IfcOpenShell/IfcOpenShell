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
import ifcopenshell.util.element
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.spatial.data import SpatialData
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
from bonsai.bim.module.aggregate.decorator import AggregateDecorator, AggregateModeDecorator


def can_aggregate(relating_obj: bpy.types.Object, related_obj: bpy.types.Object) -> bool:
    if related_obj == relating_obj:
        return False
    # Just a quick way to ignore body representations.
    if relating_obj.type != "EMPTY":
        return False
    if not tool.Aggregate.can_aggregate(relating_obj, related_obj):
        return False
    return True


def poll_relating_object(self: "BIMObjectAggregateProperties", relating_obj: bpy.types.Object) -> bool:
    if (tool.Ifc.get_entity(relating_obj)) is None:
        return False

    for related_obj_ in tool.Blender.get_selected_objects():
        if not can_aggregate(relating_obj, related_obj_):
            return False
    return True


def poll_related_object(self: "BIMObjectAggregateProperties", related_obj: bpy.types.Object) -> bool:
    if (element := tool.Ifc.get_entity(related_obj)) is None:
        return False

    aggregate = ifcopenshell.util.element.get_aggregate(element)
    if not aggregate:
        return False
    relating_obj = tool.Ifc.get_object(aggregate)
    assert isinstance(relating_obj, bpy.types.Object)

    for related_obj_ in tool.Blender.get_selected_objects():
        if related_obj_ == related_obj:
            return False
        if not can_aggregate(relating_obj, related_obj_):
            return False
    return True


def update_aggregate_decorator(self, context):
    if self.aggregate_decorator:
        AggregateDecorator.install(bpy.context)
    else:
        AggregateDecorator.uninstall()


def update_aggregate_mode_decorator(self, context):
    if self.in_aggregate_mode:
        AggregateModeDecorator.install(bpy.context)
    else:
        AggregateModeDecorator.uninstall()


class BIMObjectAggregateProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    relating_object: PointerProperty(name="Relating Whole", type=bpy.types.Object, poll=poll_relating_object)
    related_object: PointerProperty(
        name="Related Part",
        description="Related Part, will be used to derive the Relating Object",
        type=bpy.types.Object,
        poll=poll_related_object,
    )


class NotEditingObjects(bpy.types.PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object)


class BIMAggregateProperties(PropertyGroup):
    in_aggregate_mode: BoolProperty(name="In Edit Mode", update=update_aggregate_mode_decorator)
    editing_aggregate: PointerProperty(name="Editing Aggregate", type=bpy.types.Object)
    not_editing_objects: CollectionProperty(type=NotEditingObjects)
    aggregate_decorator: BoolProperty(
        name="Display Aggregate",
        default=False,
        update=update_aggregate_decorator,
    )
