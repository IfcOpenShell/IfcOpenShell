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
import ifcopenshell.util.unit
import ifcopenshell.util.element
from typing import Any


def edit_cost_value(
    file: ifcopenshell.file, cost_value: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcCostValue

    For more information about the attributes and data types of an
    IfcCostValue, consult the IFC documentation.

    :param cost_value: The IfcCostValue entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # This cost item will have a total cost of 42
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 42.0})
    """
    for name, value in attributes.items():
        if name == "AppliedValue" and value is not None:
            # TODO: support all applied value select types
            value = file.createIfcMonetaryMeasure(value)
        elif name == "UnitBasis":
            old_unit_basis = cost_value.UnitBasis
            if value:
                value_component = file.create_entity(
                    ifcopenshell.util.unit.get_unit_measure_class(value["UnitComponent"].UnitType),
                    value["ValueComponent"],
                )
                value = file.create_entity("IfcMeasureWithUnit", value_component, value["UnitComponent"])
            if old_unit_basis and file.get_total_inverses(old_unit_basis) == 0:
                ifcopenshell.util.element.remove_deep(file, old_unit_basis)
        setattr(cost_value, name, value)
