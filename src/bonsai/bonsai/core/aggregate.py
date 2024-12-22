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
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def enable_editing_aggregate(aggregator: tool.Aggregate, obj: bpy.types.Object) -> None:
    aggregator.enable_editing(obj)


def disable_editing_aggregate(aggregator: tool.Aggregate, obj: bpy.types.Object) -> None:
    aggregator.disable_editing(obj)


def assign_object(
    ifc: tool.Ifc,
    aggregator: tool.Aggregate,
    collector: tool.Collector,
    relating_obj: Optional[bpy.types.Object] = None,
    related_obj: Optional[bpy.types.Object] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    if not aggregator.can_aggregate(relating_obj, related_obj):
        raise IncompatibleAggregateError
    relating_object = ifc.get_entity(relating_obj)
    if aggregator.has_physical_body_representation(relating_object):
        raise AggregateRepresentationError
    rel = ifc.run("aggregate.assign_object", products=[ifc.get_entity(related_obj)], relating_object=relating_object)
    collector.assign(relating_obj)
    collector.assign(related_obj)
    aggregator.disable_editing(related_obj)
    return rel


def unassign_object(
    ifc: tool.Ifc,
    aggregate: tool.Aggregate,
    collector: tool.Collector,
    relating_obj: Optional[bpy.types.Object] = None,
    related_obj: Optional[bpy.types.Object] = None,
) -> None:
    related_element = ifc.get_entity(related_obj)
    container = aggregate.get_container(related_element)
    if not relating_obj:
        relating_element = aggregate.get_relating_object(related_element)
        if related_element:
            relating_obj = ifc.get_object(relating_element)
    if relating_obj:
        ifc.run("aggregate.unassign_object", products=[related_element])
        if container:
            ifc.run("spatial.assign_container", products=[related_element], relating_structure=container)
        collector.assign(relating_obj)
        collector.assign(related_obj)


def add_part_to_object(
    ifc: tool.Ifc,
    aggregator: tool.Aggregate,
    collector: tool.Collector,
    blender: tool.Blender,
    obj: bpy.types.Object,
    part_class: str,
    part_name: Optional[str] = None,
) -> None:
    part_obj = blender.create_ifc_object(ifc_class=part_class, name=part_name)
    assign_object(ifc, aggregator, collector, relating_obj=obj, related_obj=part_obj)
    blender.set_active_object(obj)

def enable_aggregate_mode(aggregator: tool.Aggregate, obj: bpy.types.Object,):
    if aggregator.get_aggregate_mode():
        disable_aggregate_mode(aggregator)

    aggregator.enable_aggregate_mode(obj)

def disable_aggregate_mode(aggregator: tool.Aggregate):
    aggregator.disable_aggregate_mode()


class IncompatibleAggregateError(Exception):
    pass


class AggregateRepresentationError(Exception):
    pass
