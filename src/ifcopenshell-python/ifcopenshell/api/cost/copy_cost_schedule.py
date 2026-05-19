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

import ifcopenshell.api.control
import ifcopenshell.api.cost
import ifcopenshell.util.element


def copy_cost_schedule(
    file: ifcopenshell.file, cost_schedule: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """Copy a cost schedule.

    :param cost_schedule: IfcCostSchedule to copy.
    :return: The duplicated IfcCostSchedule entity

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        new_schedule = ifcopenshell.api.cost.copy_cost_schedule(schedule)
    """
    # Shared code logic with copy_work_schedule.
    new_schedule = ifcopenshell.util.element.copy(file, cost_schedule)

    for rel in cost_schedule.Controls:
        for cost_item in rel.RelatedObjects:
            duplicated_cost_item = ifcopenshell.api.cost.copy_cost_item(file, cost_item)
            if isinstance(duplicated_cost_item, list):
                # All other nested items are not connected to the cost schedule explicitly.
                duplicated_cost_item = duplicated_cost_item[0]
            ifcopenshell.api.control.assign_control(file, new_schedule, [duplicated_cost_item])
    return new_schedule
