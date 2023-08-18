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

import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, work_time=None, attributes=None):
        """Edits the attributes of an IfcWorkTime

        For more information about the attributes and data types of an
        IfcWorkTime, consult the IFC documentation.

        :param work_time: The IfcWorkTime entity you want to edit
        :type work_time: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's create a new calendar.
            calendar = ifcopenshell.api.run("sequence.add_work_calendar", model)

            # Let's start defining the times that we work during the week.
            work_time = ifcopenshell.api.run("sequence.add_work_time", model,
                work_calendar=calendar, time_type="WorkingTimes")

            # If we don't specify any recurring time periods in our work time,
            # we need to specify a start and end date of the work time. It
            # starts at 0:00 on the start date and 24:00 at the end date.
            ifcopenshell.api.run("sequence.edit_work_time", model,
                work_time=work_time, attributes={"StartDate": "2000-01-01", "FinishDate": "2000-01-02"})
        """
        self.file = file
        self.settings = {"work_time": work_time, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if value and name in ["Start", "Finish"]:
                value = ifcopenshell.util.date.datetime2ifc(value, "IfcDate")
                if self.file.schema == "IFC4X3":
                    name += "Date"
            setattr(self.settings["work_time"], name, value)
