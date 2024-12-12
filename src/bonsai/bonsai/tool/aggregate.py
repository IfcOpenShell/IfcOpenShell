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
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.util.element
import ifcopenshell.util.representation
from typing import Union


class Aggregate(bonsai.core.tool.Aggregate):
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
        obj.BIMObjectAggregateProperties.is_editing = False

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        obj.BIMObjectAggregateProperties.is_editing = True

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
    def get_parts_recursively(cls, element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        parts = set()
        queue = {element}
        while queue:
            element = queue.pop()
            queue.update(new_parts := set(ifcopenshell.util.element.get_parts(element)))
            parts.update(new_parts)
        return parts

    @classmethod
    def constrain_parts_to_aggregate(cls, aggregate: bpy.types.Object):
        agg_element = tool.Ifc.get_entity(aggregate)
        parts = ifcopenshell.util.element.get_parts(agg_element)
        parts_objs = [tool.Ifc.get_object(p) for p in parts]
        for obj in parts_objs:
            constraint = next((c for c in obj.constraints if c.type == "CHILD_OF"), None)
            if constraint:
                try:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.constraint.apply(constraint="Child Of")
                except:
                    pass
            constraint = obj.constraints.new("CHILD_OF")
            constraint.target = aggregate

    @classmethod
    def apply_constraints(cls, part: bpy.types.Object):
        constraint = next((c for c in part.constraints if c.type == "CHILD_OF"), None)
        if constraint:
            bpy.context.view_layer.objects.active = part
            bpy.ops.constraint.apply(constraint=constraint.name)
            
    @classmethod
    def get_aggregate_mode(cls):
        return bpy.context.scene.BIMAggregateProperties.in_aggregate_mode

    @classmethod
    def enable_aggregate_mode(cls, active_object: bpy.types.Object):
        context = bpy.context
        props = context.scene.BIMAggregateProperties

        element = tool.Ifc.get_entity(active_object)
        if not element:
            return {"FINISHED"}
        aggregate = ifcopenshell.util.element.get_aggregate(element)
        parts = ifcopenshell.util.element.get_parts(element)
        if not aggregate and not parts:
            return {"FINISHED"}
        if not parts:
            parts = ifcopenshell.util.element.get_parts(aggregate)
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
                    obj.original.display_type = "WIRE"
                    not_editing_obj = props.not_editing_objects.add()
                    not_editing_obj.obj = obj.original
                else:
                    editing_obj = props.editing_objects.add()
                    editing_obj.obj = obj.original
                    tool.Aggregate.apply_constraints(obj.original)

        props.in_aggregate_mode = True
        return {"FINISHED"}

    @classmethod
    def disable_aggregate_mode(cls):
        context = bpy.context
        props = context.scene.BIMAggregateProperties
        objs = [o.obj for o in props.not_editing_objects]
        for obj in objs:
            obj.original.display_type = "TEXTURED"
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

        tool.Aggregate.constrain_parts_to_aggregate(props.editing_aggregate)
        props.in_aggregate_mode = False
        props.not_editing_objects.clear()
        props.editing_objects.clear()
