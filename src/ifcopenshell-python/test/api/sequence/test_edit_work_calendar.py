# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
# This file was generated with the assistance of an AI coding tool.

import datetime

import ifcopenshell.api.sequence
import ifcopenshell.util.sequence
import test.bootstrap


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestEditWorkCalendar(test.bootstrap.IFC4):
    def test_editing_exception_times_updates_calculated_working_days(self):
        self.file.create_entity("IfcProject")
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=work_time)
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file, recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]}
        )
        exception_time = ifcopenshell.api.sequence.add_work_time(
            self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        exception_pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=exception_time)
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file, recurrence_pattern=exception_pattern, attributes={"WeekdayComponent": [1]}
        )
        start = datetime.date(2020, 1, 1)
        finish = datetime.date(2020, 1, 14)
        assert ifcopenshell.util.sequence.count_working_days(start, finish, calendar) == 8

        ifcopenshell.api.sequence.edit_work_calendar(
            self.file, work_calendar=calendar, attributes={"ExceptionTimes": None}
        )
        assert ifcopenshell.util.sequence.count_working_days(start, finish, calendar) == 10


class TestEditWorkCalendarIFC4X3(test.bootstrap.IFC4X3, TestEditWorkCalendar):
    pass
