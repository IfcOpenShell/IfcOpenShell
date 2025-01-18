# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import ifcopenshell.util.element
from typing import Literal


def add_boolean(
    file: ifcopenshell.file,
    first_item: ifcopenshell.entity_instance,
    second_items: list[ifcopenshell.entity_instance],
    operator: Literal["DIFFERENCE", "INTERSECTION", "UNION"] = "DIFFERENCE",
) -> list[ifcopenshell.entity_instance]:
    """Adds a boolean operation to two or more representation items

    If an IfcBooleanOperand is part of the top level items in an
    IfcShapeRepresentation, it will be removed from that level whilst being
    added to the IfcBooleanResult. This is because it is generally intuitive
    that an item is either participating in a boolean operation, or being an
    item in its own right, but not both.

    However, if an IfcBooleanOperand is part of another boolean operation
    already, it will not be removed from the existing operation. A new
    operation will be created, and therefore it will participate in two
    operations.

    This function protects against recursive booleans.

    After a boolean operation is made, since the items of
    IfcShapeRepresentation may be modified, it is not guaranteed that the
    RepresentationType is still valid. After performing all your booleans, it
    is recommended to run :func:`ifcopenshell.api.geometry.validate_csg` to
    ensure correctness.

    :param first_item: The IfcBooleanOperand that the operation is performed upon
    :param second_items: The IfcBooleanOperands that the operation will be
        performed with, in the order given of the list.
    :param operator: The type of boolean operation to perform
    :return: A list of newly created IfcBooleanResult in the order of boolean
        operations (based on the order of second items). If nothing was
        created, the list will be empty.
    """

    def is_operand(item):
        return (
            item.is_a("IfcBooleanResult")
            or item.is_a("IfcCsgPrimitive3D")
            or item.is_a("IfcHalfSpaceSolid")
            or item.is_a("IfcSolidModel")
            or item.is_a("IfcTessellatedFaceSet")
        )

    if not is_operand(first_item):
        return []

    original_first_item = first_item

    second_items = [i for i in second_items if i != first_item and is_operand(i)]

    while True:
        is_part_of_boolean = False
        for inverse in file.get_inverse(first_item):
            if inverse.is_a("IfcBooleanResult"):
                is_part_of_boolean = True
                first_item = inverse
                if inverse.FirstOperand == original_first_item and inverse.SecondOperand in second_items:
                    second_items.remove(inverse.SecondOperand)
                elif inverse.SecondOperand == original_first_item and inverse.FirstOperand in second_items:
                    second_items.remove(inverse.FirstOperand)
                break
        if not is_part_of_boolean:
            break

    if not second_items:
        return []

    # Don't replace style or aspect relationships.
    to_replace = set(
        [i for i in file.get_inverse(first_item) if i.is_a("IfcShapeRepresentation") or i.is_a("IfcBooleanResult")]
    )

    first = first_item

    booleans = []
    for second_item in second_items:
        for inverse in file.get_inverse(second_item):
            if inverse.is_a("IfcShapeRepresentation"):
                inverse.Items = list(set(inverse.Items) - {second_item})
        if first.is_a("IfcTesselatedFaceSet"):
            first.Closed = True  # For now, trust the user to do the right thing.
        if second_item.is_a("IfcTesselatedFaceSet"):
            second_item.Closed = True  # For now, trust the user to do the right thing.
        if (
            operator == "DIFFERENCE"
            and second_item.is_a("IfcHalfSpaceSolid")
            and (
                first.is_a("IfcSweptAreaSolid")
                or first.is_a("IfcSweptDiskSolid")
                or first.is_a("IfcBooleanClippingResult")
            )
        ):
            first = file.create_entity("IfcBooleanClippingResult", operator, first, second_item)
        else:
            first = file.create_entity("IfcBooleanResult", operator, first, second_item)
        booleans.append(first)

    for inverse in to_replace:
        ifcopenshell.util.element.replace_attribute(inverse, first_item, first)

    return booleans
