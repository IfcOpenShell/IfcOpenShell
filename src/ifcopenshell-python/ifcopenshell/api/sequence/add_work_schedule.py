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
    def __init__(
        self,
        file,
        name="Unnamed",
        predefined_type="NOTDEFINED",
        object_type=None,
        start_time=None,
        work_plan=None,
    ):
        """Add a new work schedule

        A work schedule is a group of tasks, where the tasks are typically
        either for maintenance or for construction scheduling.

        :param name: The name of the work schedule.
        :type name: str
        :param predefined_type: The type of schedule, chosen from ACTUAL,
            BASELINE, and PLANNED. Typically you would start with PLANNED, then
            convert to a BASELINE when changes are made with separate schedules,
            then have a parallel ACTUAL schedule.
        :type predefined_type: str
        :param start_time: The earlier start time when the schedule is relevant.
            May be represented with an ISO standard string.
        :type start_time: str,datetime.time,optional
        :param work_plan: The IfcWorkPlan the schedule will be part of. If not
            provided, the schedule will not be grouped in a work plan and would
            exist as a top level schedule in the project. This is not
            recommended.
        :type work_plan: ifcopenshell.entity_instance.entity_instance,optional
        :return: The newly created IfcWorkSchedule
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # This will hold all our construction schedules
            work_plan = ifcopenshell.api.run("sequence.add_work_plan", model, name="Construction")

            # Let's imagine this is one of our schedules in our work plan.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model,
                name="Construction Schedule A", work_plan=work_plan)

            # Add a root task to represent the design milestones, and major
            # project phases.
            ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Milestones", identification="A")
            ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Design", identification="B")
            construction = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Construction", identification="C")
        """
        self.file = file
        self.settings = {
            "name": name,
            "predefined_type": predefined_type,
            "object_type": object_type,
            "start_time": start_time or datetime.now(),
            "work_plan": work_plan,
        }

    def execute(self):
        work_schedule = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkSchedule",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        work_schedule.CreationDate = ifcopenshell.util.date.datetime2ifc(
            datetime.now(), "IfcDateTime"
        )
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        if user:
            work_schedule.Creators = [user.ThePerson]
        work_schedule.StartTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["start_time"], "IfcDateTime"
        )
        if self.settings["object_type"]:
            work_schedule.ObjectType = self.settings["object_type"]
        if self.settings["work_plan"]:
            ifcopenshell.api.run(
                "aggregate.assign_object",
                self.file,
                **{
                    "product": work_schedule,
                    "relating_object": self.settings["work_plan"],
                }
            )
        else:
            # TODO: this is an ambiguity by buildingSMART
            # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration",
                self.file,
                definition=work_schedule,
                relating_context=context,
            )
        return work_schedule
