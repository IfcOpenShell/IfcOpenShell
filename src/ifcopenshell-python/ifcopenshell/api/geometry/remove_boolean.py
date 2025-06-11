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

import ifcopenshell.util.element


def remove_boolean(file: ifcopenshell.file, item: ifcopenshell.entity_instance) -> None:
    """Removes a boolean operation without deleting the operands

    The first operand will replace the boolean result itself, and the second
    operand will be reset as a top level representation item.

    This may affect the Items of IfcShapeRepresentation, so it is recommended
    to run :func:`ifcopenshell.api.geometry.validate_type` after all boolean
    modifications are complete.

    :param item: This may either be an IfcBooleanResult or an
        IfcRepresentationItem that is participating in one or more boolean
        results (in which case all are removed).
    """
    if not item.is_a("IfcBooleanResult"):
        for inverse in file.get_inverse(item):
            if inverse.is_a("IfcBooleanResult"):
                remove_boolean(file, inverse)
        return

    representations = []
    queue = list(file.get_inverse(item))
    while queue:
        inverse = queue.pop()
        if inverse.is_a("IfcShapeRepresentation"):
            representations.append(inverse)
        elif inverse.is_a("IfcBooleanResult"):
            queue.extend(file.get_inverse(inverse))
        elif inverse.is_a("IfcCsgSolid"):
            queue.extend(file.get_inverse(inverse))

    first = item.FirstOperand
    second = item.SecondOperand
    for inverse in file.get_inverse(item):
        ifcopenshell.util.element.replace_attribute(inverse, item, first)

    for representation in set(representations):
        representation.Items = list(representation.Items) + [second]

    file.remove(item)
