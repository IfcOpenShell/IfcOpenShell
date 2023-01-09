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


class Usecase:
    def __init__(self, file, cost_schedule=None):
        """Removes a cost schedule

        All associated relationships with the cost schedule are also removed,
        including all cost items.

        :param cost_schedule: The IfcCostSchedule entity you want to remove
        :type cost_schedule: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)
            ifcopenshell.api.run("cost.remove_cost_schedule", model, cost_schedule=schedule)
        """
        self.file = file
        self.settings = {"cost_schedule": cost_schedule}

    def execute(self):
        # TODO: do a deep purge
        self.file.remove(self.settings["cost_schedule"])
