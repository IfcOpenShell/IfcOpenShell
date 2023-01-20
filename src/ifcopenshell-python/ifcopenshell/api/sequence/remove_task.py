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
    def __init__(self, file, task=None):
        """Removes a task

        All subtasks are also removed recursively. Any relationships such as
        sequences or controls are also removed.

        :param task: The IfcTask to remove.
        :type task: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule. All tasks
            # need to be part of a work schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Add a root task to represent the design milestones, and major
            # project phases.
            ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Milestones", identification="A")
            design = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Design", identification="B")
            ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Construction", identification="C")

            # Ah, let's delete the design section, who needs it anyway we'll
            # just fix it on site.
            ifcopenshell.api.run("sequence.remove_task", model, task=design)
        """
        self.file = file
        self.settings = {"task": task}

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["task"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        if self.settings["task"].TaskTime:
            self.file.remove(self.settings["task"].TaskTime)
        for inverse in self.file.get_inverse(self.settings["task"]):
            if inverse.is_a("IfcRelSequence"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["task"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run(
                            "sequence.remove_task", self.file, task=related_object
                        )
                elif not inverse.RelatedObjects:
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                if (
                    inverse.RelatingControl == self.settings["task"]
                    or len(inverse.RelatedObjects) == 1
                ):
                    self.file.remove(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["task"])
                    inverse.RelatedObjects = related_objects
            elif inverse.is_a("IfcRelDefinesByProperties"):
                print(inverse.RelatingPropertyDefinition.Name)
                ifcopenshell.api.run(
                    "pset.remove_pset",
                    self.file,
                    product=self.settings["task"],
                    pset=inverse.RelatingPropertyDefinition,
                )
            elif inverse.is_a("IfcRelAssignsToProcess"):
                if (
                    inverse.RelatingProcess == self.settings["task"]
                    or len(inverse.RelatedObjects) == 1
                ):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToProduct"):
                if (
                    inverse.RelatingProduct == self.settings["task"]
                    or len(inverse.RelatedObjects) == 1
                ):
                    self.file.remove(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["task"])
                    inverse.RelatedObjects = related_objects
            elif inverse.is_a("IfcRelAssignsToProcess"):
                self.file.remove(inverse)

        self.file.remove(self.settings["task"])
