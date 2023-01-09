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
    def __init__(self, file, relating_process=None, related_process=None):
        """Removes a sequence relationship between tasks

        :param relating_process: The previous / predecessor task.
        :type relating_process: ifcopenshell.entity_instance.entity_instance
        :param related_process: The next / successor task.
        :type related_process: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule. All tasks
            # need to be part of a work schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Let's imagine a root construction task
            construction = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Construction", identification="C")

            # Let's imagine we're building 2 zones, one after another.
            zone1 = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=construction, name="Zone 1", identification="C.1")
            zone2 = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=construction, name="Zone 2", identification="C.2")

            # Zone 1 finishes, then zone 2 starts.
            ifcopenshell.api.run("sequence.assign_sequence", model, relating_process=zone1, related_process=zone2)

            # Let's make them unrelated
            ifcopenshell.api.run("sequence.unassign_sequence", model,
                relating_process=zone1, related_process=zone2)
        """
        self.file = file
        self.settings = {
            "relating_process": relating_process,
            "related_process": related_process,
        }

    def execute(self):
        for rel in self.settings["related_process"].IsSuccessorFrom or []:
            if rel.RelatingProcess == self.settings["relating_process"]:
                self.file.remove(rel)
        ifcopenshell.api.run(
            "sequence.cascade_schedule",
            self.file,
            task=self.settings["related_process"],
        )
