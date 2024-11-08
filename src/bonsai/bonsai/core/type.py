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
import bonsai.core.geometry
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def assign_type(
    ifc: tool.Ifc, type_tool: tool.Type, element: ifcopenshell.entity_instance, type: ifcopenshell.entity_instance
) -> None:
    ifc.run("type.assign_type", related_objects=[element], relating_type=type)
    obj = ifc.get_object(element)
    if type_tool.has_material_usage(element):
        pass  # for now, representation regeneration handled by API listeners
    else:
        type_data = type_tool.get_object_data(ifc.get_object(type))
        if type_data:
            type_tool.change_object_data(obj, type_data, is_global=False)
    type_tool.disable_editing(obj)


def purge_unused_types(ifc: tool.Ifc, type: tool.Type, geometry: tool.Geometry) -> int:
    """Remove all types without occurrences, return an amount of the removed types."""
    purged_types = 0
    for element_type in type.get_model_types():
        if not type.get_type_occurrences(element_type):
            obj = ifc.get_object(element_type)
            if obj:
                geometry.delete_ifc_object(obj)
            else:
                ifc.run("root.remove_product", product=element_type)
            purged_types += 1
    return purged_types
