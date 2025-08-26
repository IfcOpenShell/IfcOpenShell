# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.api.geometry
import ifcopenshell.util.representation
from typing import Union


def validate_type(
    file: ifcopenshell.file,
    representation: ifcopenshell.entity_instance,
    preferred_item: Union[ifcopenshell.entity_instance, None] = None,
) -> bool:
    """Validates the RepresentationType of an IfcShapeRepresentation

    A shape representation has to identify its geometry using the
    RepresentationType attribute. For example, if it holds tessellated
    geometry, it should store "Tessellation" as its RepresentationType.

    This function checks whether or not the RepresentationType is valid. This
    is a wrapper around :func:`ifcopenshell.util.representation.guess_type`. It
    will then set RepresentationType to the most appropriate value, or return
    False otherwise. In addition, it also attempts to reconcile otherwise
    invalid CSG geometry by unioning all remaining top level items to existing
    boolean results.

    :param representation: The IfcShapeRepresentation with Items
    :param preferred_item: If the type is expected to be a CSG, this will be
        the preferred item to union all remaining items to. If no preferred
        item is provided, the first boolean result will be chosen.
    :return: True if the representation type was set and it is a valid
        combination, or False otherwise.
    """

    def is_operand(item: ifcopenshell.entity_instance) -> bool:
        return (
            item.is_a("IfcBooleanResult")
            or item.is_a("IfcCsgPrimitive3D")
            or item.is_a("IfcHalfSpaceSolid")
            or item.is_a("IfcSolidModel")
            or item.is_a("IfcTessellatedFaceSet")
        )

    has_boolean = False
    remaining_items = []
    for item in representation.Items:
        if item.is_a("IfcBooleanResult"):
            has_boolean = True
        if item != preferred_item and is_operand(item):
            remaining_items.append(item)

    if not has_boolean:
        result = ifcopenshell.util.representation.guess_type(representation.Items)
        if result:
            representation.RepresentationType = result
            return True
        return False

    if not preferred_item:
        # Prioritise an existing boolean result
        for i in remaining_items:
            if i.is_a("IfcBooleanResult"):
                preferred_item = i
                break
        if not preferred_item and remaining_items:
            preferred_item = remaining_items[0]

    if remaining_items:
        ifcopenshell.api.geometry.add_boolean(file, preferred_item, remaining_items, "UNION")

    representation.RepresentationType = ifcopenshell.util.representation.guess_type(representation.Items)
    if representation.RepresentationType == "CSG":
        return True
    return False
