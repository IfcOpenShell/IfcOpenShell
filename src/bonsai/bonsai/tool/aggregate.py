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
