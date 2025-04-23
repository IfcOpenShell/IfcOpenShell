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

import ifcopenshell.api.root
import ifcopenshell.util.date
from datetime import datetime
from typing import Optional


def add_cost_schedule(
    file: ifcopenshell.file, name: Optional[str] = None, predefined_type: str = "NOTDEFINED"
) -> ifcopenshell.entity_instance:
    """Add a new cost schedule

    A cost schedule is a group of cost items which typically represent a
    cost plan or breakdown of the project. This may be used as an estimate,
    bid, or actual cost.

    Alternatively, a cost schedule may also represent a schedule of rates,
    which include cost items which capture unit rates for different elements
    or processes.

    As such, creating a cost schedule is necessary prior to creating and
    managing any cost items.

    :param name: The name of the cost schedule.
    :param predefined_type: The predefined type of the cost schedule, chosen
        from a valid type in the IFC documentation for
        IfcCostScheduleTypeEnum
    :return: The newly created IfcCostSchedule entity

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        # Now that we have a cost schedule, we may add cost items to it
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
    """
    cost_schedule = ifcopenshell.api.root.create_entity(
        file,
        ifc_class="IfcCostSchedule",
        predefined_type=predefined_type,
        name=name,
    )
    if file.schema == "IFC2X3":
        cost_schedule.UpdateDate = createIfcDateAndTime(file, datetime.now())
    else:
        cost_schedule.UpdateDate = ifcopenshell.util.date.datetime2ifc(datetime.now(), "IfcDateTime")
    return cost_schedule


def createIfcDateAndTime(file: ifcopenshell.file, dt: datetime):
    ifc_dt = file.create_entity("IfcDateAndTime")
    ifc_dt.DateComponent = file.create_entity(
        "IfcCalendarDate", **ifcopenshell.util.date.datetime2ifc(dt, "IfcCalendarDate")
    )
    ifc_dt.TimeComponent = file.create_entity("IfcLocalTime", **ifcopenshell.util.date.datetime2ifc(dt, "IfcLocalTime"))
    return ifc_dt
