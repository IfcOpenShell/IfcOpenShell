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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell

    import bonsai.tool as tool


def assign_type(
    ifc: type[tool.Ifc],
    model: type[tool.Model],
    type_tool: type[tool.Type],
    element: ifcopenshell.entity_instance,
    type: ifcopenshell.entity_instance,
) -> None:
    import ifcopenshell.util.element
    import ifcopenshell.util.representation

    # A per-instance profile occurrence (its own non-mapped body + own profile usage) should keep its
    # own geometry/length when reassigned to another type. Mapping the new type's shared representation
    # over it (the default) would convert it to typed/length-driven. Detect this and skip the mapping.
    def _is_per_instance_profile(el: ifcopenshell.entity_instance) -> bool:
        mat = ifcopenshell.util.element.get_material(el, should_inherit=False)
        if not (mat and "Profile" in mat.is_a()):
            return False
        body = ifcopenshell.util.representation.get_representation(el, "Model", "Body", "MODEL_VIEW")
        return bool(body) and not any(i.is_a("IfcMappedItem") for i in (body.Items or []))

    should_map = not _is_per_instance_profile(element)
    usage_attributes = type_tool.record_material_usage_attributes(element)
    ifc.run(
        "type.assign_type",
        related_objects=[element],
        relating_type=type,
        should_map_representations=should_map,
    )
    obj = ifc.get_object(element)
    if (usage := model.get_usage_type(type)) and usage_attributes:
        type_tool.restore_material_usage_attributes(element, usage_attributes)
    if (usage := model.get_usage_type(type)) == "PROFILE":
        model.regenerate_profile(obj)
    elif usage == "LAYER2":
        model.recalculate_walls([obj])
    elif usage == "LAYER3":
        model.regenerate_slab(obj)
    else:
        type_data = type_tool.get_object_data(ifc.get_object(type))
        if type_data:
            type_tool.change_object_data(obj, type_data, is_global=False)
    type_tool.disable_editing(obj)


def purge_unused_types(ifc: type[tool.Ifc], type: type[tool.Type], geometry: type[tool.Geometry]) -> int:
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
