# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
from typing import Any


def edit_named_unit(file: ifcopenshell.file, unit: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edits the attributes of an IfcNamedUnit

    Named units include SI units, conversion based units (imperial units),
    and context dependent units.

    For more information about the attributes and data types of an
    IfcNamedUnit, consult the IFC documentation.

    :param unit: The IfcNamedUnit entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        # Boxes of things
        unit = ifcopenshell.api.unit.add_context_dependent_unit(model, name="BOXES")

        # Uh, crates? Boxes? Whatever.
        ifcopenshell.api.unit.edit_named_unit(model, unit=unit, attibutes={"Name": "CRATES"})
    """
    for name, value in attributes.items():
        if name == "Dimensions":
            dimensions = unit.Dimensions
            if file.get_total_inverses(dimensions) > 1:
                unit.Dimensions = file.createIfcDimensionalExponents(*value)
            else:
                for i, exponent in enumerate(value):
                    dimensions[i] = exponent
            continue
        setattr(unit, name, value)
