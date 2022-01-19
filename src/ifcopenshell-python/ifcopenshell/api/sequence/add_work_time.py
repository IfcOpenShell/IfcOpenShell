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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_calendar": None, "time_type": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_time = self.file.create_entity("IfcWorkTime")
        if self.settings["time_type"] == "WorkingTimes":
            working_times = list(self.settings["work_calendar"].WorkingTimes or [])
            working_times.append(work_time)
            self.settings["work_calendar"].WorkingTimes = working_times
        elif self.settings["time_type"] == "ExceptionTimes":
            exception_times = list(self.settings["work_calendar"].ExceptionTimes or [])
            exception_times.append(work_time)
            self.settings["work_calendar"].ExceptionTimes = exception_times
        return work_time
