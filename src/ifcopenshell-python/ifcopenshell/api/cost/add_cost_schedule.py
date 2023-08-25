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

import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime


class Usecase:
    def __init__(self, file, name=None, predefined_type="NOTDEFINED", object_type=None):
        """Add a new cost schedule

        A cost schedule is a group of cost items which typically represent a
        cost plan or breakdown of the project. This may be used as an estimate,
        bid, or actual cost.

        Alternatively, a cost schedule may also represent a schedule of rates,
        which include cost items which capture unit rates for different elements
        or processes.

        As such, creating a cost schedule is necessary prior to creating and
        managing any cost items.

        :param name: The name of the cost schedule.
        :type name: str, optional
        :param predefined_type: The predefined type of the cost schedule, chosen
            from a valid type in the IFC documentation for
            IfcCostScheduleTypeEnum
        :type predefined_type: str, optional
        :return: The newly created IfcCostSchedule entity
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            # Now that we have a cost schedule, we may add cost items to it
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)
        """
        self.file = file
        self.settings = {"name": name, "predefined_type": predefined_type, "object_type": object_type}

    def execute(self):
        cost_schedule = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcCostSchedule",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        cost_schedule.UpdateDate = ifcopenshell.util.date.datetime2ifc(datetime.now(), "IfcDateTime")
        if self.settings["object_type"]:
            cost_schedule.ObjectType = self.settings["object_type"]
        return cost_schedule
