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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, work_schedule=None, work_plan=None):
        """Assigns a work schedule to a work plan

        Typically, work schedules would be assigned to a work plan at creation.
        However you may also delay this and do it manually afterwards.

        :param work_schedule: The IfcWorkSchedule that will be assigned to the
            work plan.
        :type work_schedule: ifcopenshell.entity_instance.entity_instance
        :param work_plan: The IfcWorkPlan for the schedule to be assigned to.
        :type work_plan: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAggregates relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # This will hold all our construction schedules
            work_plan = ifcopenshell.api.run("sequence.add_work_plan", model, name="Construction")

            # Alternatively, if you create a schedule without a work plan ...
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # ... you can assign the work plan afterwards.
            ifcopenshell.api.run("sequence.assign_workplan", work_schedule=schedule, work_plan=work_plan)
        """
        self.file = file
        self.settings = {"work_schedule": work_schedule, "work_plan": work_plan}

    def execute(self):
        # TODO: this is an ambiguity by buildingSMART
        # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["work_schedule"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        rel_aggregates = ifcopenshell.api.run(
            "aggregate.assign_object",
            self.file,
            **{
                "product": self.settings["work_schedule"],
                "relating_object": self.settings["work_plan"],
            }
        )
        return rel_aggregates
