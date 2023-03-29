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
    def __init__(self, file, name=None, predefined_type="NOTDEFINED", start_time=None):
        """Add a new work plan

        A work plan is a group of work schedules. Since work schedules may have
        different purposes, such as for maintenance or construction scheduling,
        baseline comparison, or phasing, work plans can be used to group related
        work schedules. At a minimum, it is recommended to use work plans to
        indicate whether the work schedules are for facility management or for
        construction scheduling.

        :param name: The name of the work plan. Recommended to be "Maintenance"
            or "Construction" for the two main purposes.
        :type name: str, optional
        :param predefined_type: The type of work plan, used for baselining.
            Leave as "NOTDEFINED" if unsure.
        :type predefined_type: str
        :param start_time: The earliest start time when the schedules grouped
            within the work plan are relevant.
        :type start_time: str,datetime.time
        :return: The newly created IfcWorkPlan
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # This will hold all our construction schedules
            work_plan = ifcopenshell.api.run("sequence.add_work_plan", model, name="Construction")

            # This is one of our schedules in our work plan.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model,
                name="Construction Schedule A", work_plan=work_plan)
        """
        self.file = file
        self.settings = {
            "name": name,
            "predefined_type": predefined_type,
            "start_time": start_time or datetime.now(),
        }

    def execute(self):
        work_plan = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkPlan",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        work_plan.CreationDate = ifcopenshell.util.date.datetime2ifc(
            datetime.now(), "IfcDateTime"
        )
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        if user:
            work_plan.Creators = [user.ThePerson]
        work_plan.StartTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["start_time"], "IfcDateTime"
        )

        context = self.file.by_type("IfcContext")[0]
        ifcopenshell.api.run(
            "project.assign_declaration",
            self.file,
            definition=work_plan,
            relating_context=context,
        )
        return work_plan
