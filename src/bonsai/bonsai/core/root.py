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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def copy_class(
    ifc: tool.Ifc, collector: tool.Collector, geometry: tool.Geometry, root: tool.Root, obj: bpy.types.Object
) -> ifcopenshell.entity_instance:
    element = ifc.get_entity(obj)
    if not element:
        return
    if root.is_element_a(element, "IfcRelSpaceBoundary"):
        new = ifc.run("boundary.copy_boundary", boundary=element)
        ifc.link(new, obj)
        return new
    representation = root.get_object_representation(obj)
    new = ifc.run("root.copy_class", product=element)
    ifc.link(new, obj)
    relating_type = root.get_element_type(new)
    if relating_type and root.does_type_have_representations(relating_type):
        ifc.run("type.map_type_representations", related_object=new, relating_type=relating_type)
        root.link_object_data(ifc.get_object(relating_type), obj)
    elif representation:
        root.copy_representation(element, new)
        new_representation = root.get_element_representation(new, root.get_representation_context(representation))
        data = geometry.duplicate_object_data(obj)
        if data:
            geometry.change_object_data(obj, data, is_global=True)
            geometry.rename_object(data, geometry.get_representation_name(new_representation))
            geometry.link(new_representation, data)
            geometry.reload_representation_item_ids(new_representation, data)
        root.assign_body_styles(new, obj)
    collector.assign(obj)
    if root.is_element_a(new, "IfcOpeningElement"):
        root.add_tracked_opening(obj)
    return new


def assign_class(
    ifc: tool.Ifc,
    collector: tool.Collector,
    root: tool.Root,
    obj: bpy.types.Object,
    ifc_class: str,
    context: Optional[ifcopenshell.entity_instance] = None,
    predefined_type: Optional[str] = None,
    should_add_representation: bool = True,
    ifc_representation_class: Optional[str] = None,
) -> Optional[ifcopenshell.entity_instance]:
    """
    Args:
        context: is not optional if `should_add_representation` is True
    """
    if ifc.get_entity(obj):
        return

    name = root.get_object_name(obj)
    element = ifc.run("root.create_entity", ifc_class=ifc_class, predefined_type=predefined_type, name=name)
    root.set_object_name(obj, element)
    ifc.link(element, obj)

    if should_add_representation:
        assert context, "Context is required for adding a representation"
        root.run_geometry_add_representation(
            obj=obj, context=context, ifc_representation_class=ifc_representation_class, profile_set_usage=None
        )

    if not root.is_drawing_annotation(element) and (default_container := root.get_default_container()):
        if root.is_spatial_element(element):
            ifc.run("aggregate.assign_object", products=[element], relating_object=default_container)
        elif root.is_containable(element):
            ifc.run("spatial.assign_container", products=[element], relating_structure=default_container)
    collector.assign(obj)
    return element
