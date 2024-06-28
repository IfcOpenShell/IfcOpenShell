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
import ifcopenshell.api.cost
import ifcopenshell.util.element


def remove_cost_schedule(file: ifcopenshell.file, cost_schedule: ifcopenshell.entity_instance) -> None:
    """Removes a cost schedule

    All associated relationships with the cost schedule are also removed,
    including all cost items.

    :param cost_schedule: The IfcCostSchedule entity you want to remove
    :type cost_schedule: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        ifcopenshell.api.cost.remove_cost_schedule(model, cost_schedule=schedule)
    """
    settings = {"cost_schedule": cost_schedule}

    # TODO: do a deep purge
    for inverse in file.get_inverse(settings["cost_schedule"]):
        if inverse.is_a("IfcRelAssignsToControl"):
            [
                ifcopenshell.api.cost.remove_cost_item(file, cost_item=related_object)
                for related_object in inverse.RelatedObjects
                if related_object.is_a("IfcCostItem")
            ]
    history = settings["cost_schedule"].OwnerHistory
    file.remove(settings["cost_schedule"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
