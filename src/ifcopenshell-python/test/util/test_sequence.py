# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 myoualid
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

import datetime

import ifcopenshell.api.root
import ifcopenshell.api.sequence
import ifcopenshell.util.sequence as subject
import test.bootstrap

H = datetime.timedelta(hours=1)
MONDAY = datetime.date(2026, 1, 19)
SATURDAY = datetime.date(2026, 1, 24)


def add_calendar(file, periods=None, weekdays=(1, 2, 3, 4, 5)):
    if not file.by_type("IfcProject"):
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
    calendar = ifcopenshell.api.sequence.add_work_calendar(file)
    work_time = ifcopenshell.api.sequence.add_work_time(file, work_calendar=calendar)
    pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(file, parent=work_time, recurrence_type="WEEKLY")
    ifcopenshell.api.sequence.edit_recurrence_pattern(
        file, recurrence_pattern=pattern, attributes={"WeekdayComponent": list(weekdays)}
    )
    for start, end in periods or []:
        ifcopenshell.api.sequence.add_time_period(file, recurrence_pattern=pattern, start_time=start, end_time=end)
    return calendar


class TestGetWorkPeriods(test.bootstrap.IFC4):
    def test_reading_the_time_periods_of_the_calendar(self):
        calendar = add_calendar(self.file, [("13:00:00", "17:00:00"), ("07:00:00", "12:00:00")])
        assert subject.get_work_periods(MONDAY, calendar) == [(7 * H, 12 * H), (13 * H, 17 * H)]

    def test_using_one_period_from_9_if_there_is_no_time_period(self):
        calendar = add_calendar(self.file)
        assert subject.get_work_periods(MONDAY, calendar) == [(9 * H, 17 * H)]
        assert subject.get_work_periods(MONDAY, None, 10 * H) == [(9 * H, 19 * H)]

    def test_returning_no_period_on_a_day_without_work(self):
        calendar = add_calendar(self.file, [("07:00:00", "12:00:00")])
        assert subject.get_work_periods(SATURDAY, calendar) == []
