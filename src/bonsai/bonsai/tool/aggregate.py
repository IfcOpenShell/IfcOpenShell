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
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.util.element
import ifcopenshell.util.representation
from typing import Union, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from bonsai.bim.module.aggregate.prop import BIMAggregateProperties, BIMObjectAggregateProperties


class Aggregate(bonsai.core.tool.Aggregate):
    @classmethod
    def get_aggregate_props(cls) -> BIMAggregateProperties:
        return bpy.context.scene.BIMAggregateProperties

    @classmethod
    def get_object_aggregate_props(cls, obj: bpy.types.Object) -> BIMObjectAggregateProperties:
        return obj.BIMObjectAggregateProperties

    @classmethod
    def can_aggregate(cls, relating_obj: bpy.types.Object, related_obj: bpy.types.Object) -> bool:
        relating_object = tool.Ifc.get_entity(relating_obj)
        related_object = tool.Ifc.get_entity(related_obj)
        if not relating_object or not related_object:
            return False
        if (relating_object.is_a("IfcElement") or relating_object.is_a("IfcElementType")) and related_object.is_a(
            "IfcElement"
        ):
            return True
        if tool.Ifc.get_schema() == "IFC2X3":
            if relating_object.is_a("IfcSpatialStructureElement") and related_object.is_a("IfcSpatialStructureElement"):
                return True
            if relating_object.is_a("IfcProject") and related_object.is_a("IfcSpatialStructureElement"):
                return True
        else:
            if relating_object.is_a("IfcSpatialElement") and related_object.is_a("IfcSpatialElement"):
                return True
            if relating_object.is_a("IfcProject") and related_object.is_a("IfcSpatialElement"):
                return True
        return False

    @classmethod
    def has_physical_body_representation(cls, element: ifcopenshell.entity_instance) -> bool:
        if element.is_a("IfcElement") or element.is_a("IfcElementType"):  # See 3973
            if ifcopenshell.util.representation.get_representation(element, "Model", "Body"):
                return True
        return False

    @classmethod
    def disable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_aggregate_props(obj)
        props.is_editing = False

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_aggregate_props(obj)
        props.is_editing = True

    @classmethod
    def get_container(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_relating_object(
        cls, related_element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        for rel in related_element.Decomposes:
            if rel.is_a("IfcRelAggregates"):
                return rel.RelatingObject

    @classmethod
    def get_aggregates_recursively(cls, element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        """Get elements aggregates recursively, resulting set includes `element`."""
        aggregates = list()
        queue = {element}
        while queue:
            element = queue.pop()
            aggregate = ifcopenshell.util.element.get_aggregate(element)
            if aggregate:
                queue.update({aggregate})
            if ifcopenshell.util.element.get_parts(element):
                aggregates.append(element)
        return aggregates

    @classmethod
    def get_parts_recursively(cls, element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        """Get elements parts recursively, resulting set includes `element`."""
        parts = set()
        queue = {element}
        while queue:
            element = queue.pop()
            queue.update(new_parts := set(ifcopenshell.util.element.get_parts(element)))
            parts.update(new_parts)
        return parts

    @classmethod
    def get_higher_aggregate(cls) -> ifcopenshell.entity_instance:
        props = cls.get_aggregate_props()
        editing_aggregate = tool.Ifc.get_entity(props.editing_aggregate)
        higher_aggregate = ifcopenshell.util.element.get_aggregate(editing_aggregate)
        return tool.Ifc.get_object(higher_aggregate) if higher_aggregate else None

    @classmethod
    def update_previous_aggregate_mode_state(cls):
        props = cls.get_aggregate_props()
        props.previous_state = props.in_aggregate_mode
        props.previous_editing_aggregate = props.editing_aggregate

    @classmethod
    def enable_aggregate_mode(cls, active_object: bpy.types.Object) -> set[Literal["FINISHED"]]:
        context = bpy.context
        props = cls.get_aggregate_props()

        element = tool.Ifc.get_entity(active_object)
        if not element:
            return {"FINISHED"}
        # Defines the aggregate based on previous state
        # Controls whether the user is entering a deeper level or
        # exiting to a higher level. See core/aggregate.py
        aggregates = tool.Aggregate.get_aggregates_recursively(element)
        aggregate = aggregates[-1]
        if props.previous_state:
            previous_aggregate = tool.Ifc.get_entity(props.previous_editing_aggregate)
            if previous_aggregate in aggregates:
                reference_index = aggregates.index(previous_aggregate)
                aggregate = aggregates[reference_index - 1]
            else:
                aggregate = aggregates[0]

        parts = tool.Aggregate.get_parts_recursively(element)
        if not aggregate and not parts:
            return {"FINISHED"}
        if not parts:
            parts = tool.Aggregate.get_parts_recursively(aggregate)
        if parts:
            props.editing_aggregate = tool.Ifc.get_object(aggregate) if aggregate else tool.Ifc.get_object(element)
            parts_objs = [tool.Ifc.get_object(part) for part in parts]
            objs = []
            visible_objects = tool.Raycast.get_visible_objects(context)
            for obj in visible_objects:
                if obj.visible_in_viewport_get(context.space_data):
                    objs.append(obj.original)
            for obj in objs:
                if obj.original not in parts_objs:
                    if obj == props.editing_aggregate:
                        continue
                    not_editing_obj = props.not_editing_objects.add()
                    not_editing_obj.obj = obj.original
                    not_editing_obj.previous_display_type = obj.original.display_type
                    not_editing_obj.previous_hide_select = obj.original.hide_select
                    obj.original.display_type = "WIRE"
                    obj.hide_select = True
                else:
                    editing_obj = props.editing_objects.add()
                    editing_obj.obj = obj.original

        props.in_aggregate_mode = True
        return {"FINISHED"}

    @classmethod
    def disable_aggregate_mode(cls):
        context = bpy.context
        props = cls.get_aggregate_props()
        for obj_prop in props.not_editing_objects:
            obj = obj_prop.obj
            if not obj:
                continue
            obj.original.display_type = obj_prop.previous_display_type
            obj.hide_select = obj_prop.previous_hide_select
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

        if context.space_data.local_view:
            bpy.ops.view3d.localview()

        props.in_aggregate_mode = False
        props.not_editing_objects.clear()
        props.editing_objects.clear()
        props.editing_aggregate = None
