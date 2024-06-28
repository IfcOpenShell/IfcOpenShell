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
from typing import Any


def edit_work_schedule(
    file: ifcopenshell.file, work_schedule: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcWorkSchedule

    For more information about the attributes and data types of an
    IfcWorkSchedule, consult the IFC documentation.

    :param work_schedule: The IfcWorkSchedule entity you want to edit
    :type work_schedule: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # This will hold all our construction schedules
        work_plan = ifcopenshell.api.sequence.add_work_plan(model, name="Construction")

        # Let's imagine this is one of our schedules in our work plan.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model,
            name="Construction Schedule A", work_plan=work_plan)

        # Let's give it a description
        ifcopenshell.api.sequence.edit_work_schedule(model,
            work_schedule=work_schedule, attributes={"Description": "3 crane design option"})
    """
    settings = {"work_schedule": work_schedule, "attributes": attributes}

    for name, value in settings["attributes"].items():
        if value:
            if "Date" in name or "Time" in name:
                value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
            elif name == "Duration" or name == "TotalFloat":
                value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
        setattr(settings["work_schedule"], name, value)
