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
    def __init__(self, file, task=None, attributes=None):
        """Edits the attributes of an IfcTask

        For more information about the attributes and data types of an
        IfcTask, consult the IFC documentation.

        :param task: The IfcTask entity you want to edit
        :type task: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule. All tasks
            # need to be part of a work schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Add a root task to represent the design milestones, and major
            # project phases.
            task = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Milestones", identification="A")

            # Change the identification
            ifcopenshell.api.run("sequence.edit_task", model, task=task, attributes={"Identification": "M"})
        """
        self.file = file
        self.settings = {"task": task, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["task"], name, value)
