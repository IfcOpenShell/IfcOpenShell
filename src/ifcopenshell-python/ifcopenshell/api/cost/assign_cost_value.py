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

import ifcopenshell.api.cost


def assign_cost_value(
    file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance, cost_rate: ifcopenshell.entity_instance
) -> None:
    """Assigns a cost value to a cost item from a schedule of rates

    Instead of assigning cost values from scratch for each cost item in a
    cost schedule, the cost values may instead be assigned from a schedule
    of rates.

    A schedule of rates is just another cost schedule which have cost values
    but no quantities. This API will allow you to "copy" the values from a
    cost item in the schedule of rates into another cost item in your own
    cost schedule. When the schedule of rates value is updated, then your
    cost item values will also be updated. You can think of the schedule of
    rates as a "template" to quickly populate your rates from.

    :param cost_item: The IfcCostItem that you want to copy the values to
    :param cost_rate: The IfcCostItem that you want to copy the values from
    :return: None

    Example:

    .. code:: python

        # Let's create a schedule of rates with a single rate in it of 5.0
        rate_tables = ifcopenshell.api.cost.add_cost_schedule(model,
            predefined_type="SCHEDULEOFRATES")
        rate = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=rate)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})

        # And this schedule will be for our actual cost plan / estimate / etc
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # Now the cost item has the same rate as the one from the schedule of rate's item
        ifcopenshell.api.cost.assign_cost_value(model, cost_item=item, cost_rate=rate)
    """
    if cost_item.CostValues:
        [
            ifcopenshell.api.cost.remove_cost_value(
                file,
                parent=cost_item,
                cost_value=cost_value,
            )
            for cost_value in cost_item.CostValues
        ]
    # This is an assumption, and not part of the official IFC documentation
    cost_item.CostValues = cost_rate.CostValues
