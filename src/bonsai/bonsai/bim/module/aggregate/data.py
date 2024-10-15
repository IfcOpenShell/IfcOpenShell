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
import bonsai.tool as tool
import ifcopenshell.util.element
from typing import Union


def refresh():
    AggregateData.is_loaded = False


class AggregateData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_relating_object": cls.has_relating_object(),
            "relating_object_label": cls.get_relating_object_label(),
            "has_related_objects": cls.has_related_objects(),
            "total_parts": cls.total_parts(),
            "total_linked_aggregate": cls.total_linked_aggregate(),
        }
        cls.is_loaded = True

    @classmethod
    def get_relating_object(cls):
        return ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def has_relating_object(cls) -> bool:
        return cls.get_relating_object() is not None

    @classmethod
    def get_relating_object_label(cls) -> str:
        aggregate = cls.get_relating_object()
        if aggregate:
            return f"{aggregate.is_a()}/{aggregate.Name or ''}"

    @classmethod
    def get_related_objects(cls):
        return ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def total_parts(cls):
        parts = cls.get_related_objects()
        return len(parts) if parts else 0

    @classmethod
    def has_related_objects(cls) -> bool:
        return bool(cls.get_related_objects())

    @classmethod
    def total_linked_aggregate(cls) -> Union[int, None]:
        element = tool.Ifc.get_entity(bpy.context.active_object)
        aggregate = ifcopenshell.util.element.get_aggregate(element)
        if not aggregate:
            return
        if not element:
            return

        product_linked_agg_group = next(
            (
                r
                for r in getattr(aggregate, "HasAssignments", []) or []
                if r.is_a("IfcRelAssignsToGroup")
                if "BBIM_Linked_Aggregate" in r.RelatingGroup.Name
            ),
            None,
        )

        if product_linked_agg_group is None:
            return

        total = len(product_linked_agg_group.RelatedObjects)
        return total
