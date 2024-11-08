# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


def enable_editing_nest(nest, obj=None):
    nest.enable_editing(obj)


def disable_editing_nest(nest, obj=None):
    nest.disable_editing(obj)


def assign_object(ifc, nest, collector, relating_obj=None, related_obj=None):
    if not nest.can_nest(relating_obj, related_obj):
        return
    rel = ifc.run(
        "nest.assign_object",
        related_objects=[ifc.get_entity(related_obj)],
        relating_object=ifc.get_entity(relating_obj),
    )
    collector.assign(relating_obj)
    collector.assign(related_obj)
    nest.disable_editing(related_obj)
    return rel


def unassign_object(ifc, nest, collector, relating_obj=None, related_obj=None):
    related_element = ifc.get_entity(related_obj)
    container = nest.get_container(related_element)
    if not relating_obj:
        relating_element = nest.get_relating_object(related_element)
        if related_element:
            relating_obj = ifc.get_object(relating_element)
    if relating_obj:
        ifc.run("nest.unassign_object", related_objects=[related_element])
        if container:
            ifc.run("spatial.assign_container", products=[related_element], relating_structure=container)
        collector.assign(relating_obj)
        collector.assign(related_obj)


def add_part_to_object(ifc, nest, collector, blender, obj, part_class, part_name=None):
    part_obj = blender.create_ifc_object(ifc_class=part_class, name=part_name)
    assign_object(ifc, nest, collector, relating_obj=obj, related_obj=part_obj)
    blender.set_active_object(obj)
