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


def remove_work_time(file: ifcopenshell.file, work_time: ifcopenshell.entity_instance) -> None:
    """Removes a work time

    :param work_time: The IfcWorkTime to remove.
    :type work_time: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's create a new calendar.
        calendar = ifcopenshell.api.run("sequence.add_work_calendar", model)

        # Let's start defining the times that we work during the week.
        work_time = ifcopenshell.api.run("sequence.add_work_time", model,
            work_calendar=calendar, time_type="WorkingTimes")

        # And remove it immediately
        ifcopenshell.api.run("sequence.remove_work_time", model, work_time=work_time)
    """
    settings = {"work_time": work_time}

    file.remove(settings["work_time"])
