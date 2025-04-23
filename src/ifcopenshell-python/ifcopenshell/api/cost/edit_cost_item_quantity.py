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


def edit_cost_item_quantity(
    file: ifcopenshell.file, physical_quantity: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcPhysicalQuantity

    For more information about the attributes and data types of an
    IfcPhysicalQuantity, consult the IFC documentation.

    :param physical_quantity: The IfcPhysicalQuantity entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # This cost item will have a unit cost of 5 and a volume of 3
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})
        quantity = ifcopenshell.api.cost.add_cost_item_quantity(model,
            cost_item=item, ifc_class="IfcQuantityVolume")
        ifcopenshell.api.cost.edit_cost_item_quantity(model,
            physical_quantity=quantity, "attributes": {"VolumeValue": 3.0})
    """
    for name, value in attributes.items():
        setattr(physical_quantity, name, value)
