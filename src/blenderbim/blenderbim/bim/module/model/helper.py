# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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
import bmesh
import ifcopenshell
import ifcopenshell.util.unit
import blenderbim.core.geometry as core
import blenderbim.tool as tool


def get_ifc_context_or_create(ifc_file, context_type, context_identifier, target_view):
    ifc_context = ifcopenshell.util.representation.get_context(ifc_file, context_type, context_identifier, target_view)
    if not ifc_context:
        parent_context = ifcopenshell.util.representation.get_context(ifc_file, context_type)
        ifc_context = ifcopenshell.api.run(
            "context.add_context",
            ifc_file,
            context_type=context_type,
            context_identifier=context_identifier,
            target_view=target_view,
            parent=parent_context,
        )
    return ifc_context


def replace_ifc_representation_for_object(ifc_file, ifc_context, obj, new_representation):
    ifc_element = tool.Ifc.get_entity(obj)
    old_representation = ifcopenshell.util.representation.get_representation(
        ifc_element, ifc_context.ContextType, ifc_context.ContextIdentifier, ifc_context.TargetView
    )

    if old_representation:
        old_representation = tool.Geometry.resolve_mapped_representation(old_representation)
        for inverse in ifc_file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)
        ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=old_representation)
    else:
        ifcopenshell.api.run(
            "geometry.assign_representation", ifc_file, product=ifc_element, representation=new_representation
        )
    core.switch_representation(
        tool.Ifc,
        tool.Geometry,
        obj=obj,
        representation=new_representation,
        should_reload=True,
        is_global=True,
        should_sync_changes_first=False,
    )


