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


def add_boolean(
    file: ifcopenshell.file,
    first_item: ifcopenshell.entity_instance,
    second_items: list[ifcopenshell.entity_instance],
    operator: str = "DIFFERENCE",
) -> set[ifcopenshell.entity_instance]:
    original_first_item = first_item
    if first_item in second_items:
        second_items.remove(first_item)

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
        return

    # Don't replace style or aspect relationships.
    to_replace = set(
        [
            i
            for i in file.get_inverse(first_item)
            if i.is_a("IfcShapeRepresentation") or i.is_a("IfcBooleanResult")
        ]
    )

    first = first_item

    booleans = set()
    for second_item in second_items:
        for inverse in file.get_inverse(second_item):
            if inverse.is_a("IfcShapeRepresentation"):
                inverse.Items = list(set(inverse.Items) - {second_item})
        if first.is_a("IfcTesselatedFaceSet"):
            first.Closed = True  # For now, trust the user to do the right thing.
        if second_item.is_a("IfcTesselatedFaceSet"):
            second_item.Closed = True  # For now, trust the user to do the right thing.
        first = file.create_entity("IfcBooleanResult", operator, first, second_item)
        booleans.add(first)

    for inverse in to_replace:
        ifcopenshell.util.element.replace_attribute(inverse, first_item, first)

    return booleans
