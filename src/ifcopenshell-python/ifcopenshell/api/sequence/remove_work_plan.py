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


class Usecase:
    def __init__(self, file, work_plan=None):
        """Removes a work plan

        Note that schedules that are grouped under the work plan are not
        removed.

        :param work_plan: The IfcWorkPlan to remove.
        :type work_plan: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # This will hold all our construction schedules
            work_plan = ifcopenshell.api.run("sequence.add_work_plan", model, name="Construction")

            # And remove it immediately
            ifcopenshell.api.run("sequence.remove_work_plan", model, work_plan=work_plan)
        """
        self.file = file
        self.settings = {"work_plan": work_plan}

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["work_plan"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        self.file.remove(self.settings["work_plan"])
