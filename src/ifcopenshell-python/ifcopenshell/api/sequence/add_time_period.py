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
import ifcopenshell.util.date
from datetime import datetime
from datetime import timedelta


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "recurrence_pattern": None,
            "start_time": None,
            "end_time": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        time_period = self.file.create_entity("IfcTimePeriod")
        time_period.StartTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["start_time"], "IfcTime"
        )
        time_period.EndTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["end_time"], "IfcTime"
        )
        time_periods = list(self.settings["recurrence_pattern"].TimePeriods or [])
        time_periods.append(time_period)
        self.settings["recurrence_pattern"].TimePeriods = time_periods
        return time_period
