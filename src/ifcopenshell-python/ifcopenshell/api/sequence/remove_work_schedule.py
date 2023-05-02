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


class Usecase:
    def __init__(self, file, work_schedule=None):
        """Removes a work schedule

        All tasks in the work schedule are also removed recursively.

        :param work_schedule: The IfcWorkSchedule to remove.
        :type work_schedule: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # This will hold all our construction schedules
            work_plan = ifcopenshell.api.run("sequence.add_work_plan", model, name="Construction")

            # Let's imagine this is one of our schedules in our work plan.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model,
                name="Construction Schedule A", work_plan=work_plan)

            # And remove it immediately
            ifcopenshell.api.run("sequence.remove_work_schedule", model, work_schedule=schedule)
        """
        self.file = file
        self.settings = {"work_schedule": work_schedule}

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["work_schedule"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        if self.settings["work_schedule"].Declares:
            for rel in self.settings["work_schedule"].Declares:
                for work_schedule in rel.RelatedObjects:
                    ifcopenshell.api.run(
                        "sequence.remove_work_schedule",
                        self.file,
                        work_schedule=work_schedule,
                    )
        for inverse in self.file.get_inverse(self.settings["work_schedule"]):
            if inverse.is_a("IfcRelDefinesByObject"):
                if (
                    inverse.RelatingObject == self.settings["work_schedule"]
                    or len(inverse.RelatedObjects) == 1
                ):
                    self.file.remove(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["work_schedule"])
                    inverse.RelatedObjects = related_objects
            elif inverse.is_a("IfcRelAssignsToControl"):
                [
                    ifcopenshell.api.run(
                        "sequence.remove_task", self.file, task=related_object
                    )
                    for related_object in inverse.RelatedObjects
                    if related_object.is_a("IfcTask")
                ]

        self.file.remove(self.settings["work_schedule"])
