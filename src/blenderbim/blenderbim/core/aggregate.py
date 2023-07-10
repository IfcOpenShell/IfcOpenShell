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


def enable_editing_aggregate(aggregator, obj=None):
    aggregator.enable_editing(obj)


def disable_editing_aggregate(aggregator, obj=None):
    aggregator.disable_editing(obj)


def assign_object(ifc, aggregator, collector, relating_obj=None, related_obj=None):
    if not aggregator.can_aggregate(relating_obj, related_obj):
        return
    rel = ifc.run(
        "aggregate.assign_object", product=ifc.get_entity(related_obj), relating_object=ifc.get_entity(relating_obj)
    )
    collector.assign(relating_obj)
    collector.assign(related_obj)
    aggregator.disable_editing(related_obj)
    return rel


def unassign_object(ifc, aggregate, collector, relating_obj=None, related_obj=None):
    related_element = ifc.get_entity(related_obj)
    container = aggregate.get_container(related_element)
    if not relating_obj:
        relating_element = aggregate.get_relating_object(related_element)
        if related_element:
            relating_obj = ifc.get_object(relating_element)
    if relating_obj:
        ifc.run("aggregate.unassign_object", product=related_element)
        if container:
            ifc.run("spatial.assign_container", product=related_element, relating_structure=container)
        collector.assign(relating_obj)
        collector.assign(related_obj)


def add_part_to_object(ifc, aggregator, collector, blender, obj, part_class, part_name=None):
    part_obj = blender.create_ifc_object(ifc_class=part_class, name=part_name)
    assign_object(ifc, aggregator, collector, relating_obj=obj, related_obj=part_obj)
    blender.set_active_object(obj)
