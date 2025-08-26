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
from datetime import datetime
from typing import Union


def add_date_time(file: ifcopenshell.file, dt: datetime) -> Union[str, ifcopenshell.entity_instance]:
    """Add a new date time.

    Depending on ``file``'s schema method will:
    - IFC2X3 - create IfcDateAndTime entity
    - IFC4+  - create IfcDatetime formatted string

    :param dt: datetime to convert to IFC.
    :return: IfcDateAndTime entity or IfcDatetime string.

    Example:

    .. code:: python

        dt = datetime(2025, 3, 1, 12, 31, 24)
        datetime_ifc = ifcopenshell.api.sequence.add_date_time(self.file, dt)

        # IFC2X3: #1=IfcDateAndTime(#2,#3)
        # IFC4+: "2025-03-01T12:31:24"
        print(datetime_ifc)

    """

    if file.schema == "IFC2X3":
        ifc_dt = file.create_entity("IfcDateAndTime")
        calendar_date_data = ifcopenshell.util.date.datetime2ifc(dt, "IfcCalendarDate")
        assert isinstance(calendar_date_data, dict)
        ifc_dt.DateComponent = file.create_entity("IfcCalendarDate", **calendar_date_data)
        local_time_data = ifcopenshell.util.date.datetime2ifc(dt, "IfcLocalTime")
        assert isinstance(local_time_data, dict)
        ifc_dt.TimeComponent = file.create_entity("IfcLocalTime", **local_time_data)
        return ifc_dt

    dt_str = ifcopenshell.util.date.datetime2ifc(dt, "IfcDateTime")
    assert isinstance(dt_str, str)
    return dt_str
