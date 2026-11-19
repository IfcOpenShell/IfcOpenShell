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

import ifcopenshell.api.pset
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


def add_exception(file, calendar, day, periods=None):
    work_time = ifcopenshell.api.sequence.add_work_time(file, work_calendar=calendar, time_type="ExceptionTimes")
    day_before, day_after = (day + datetime.timedelta(days=i) for i in (-1, 1))
    ifcopenshell.api.sequence.edit_work_time(
        file, work_time=work_time, attributes={"Start": day_before.isoformat(), "Finish": day_after.isoformat()}
    )
    if periods:
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(file, parent=work_time, recurrence_type="DAILY")
        for start, end in periods:
            ifcopenshell.api.sequence.add_time_period(file, recurrence_pattern=pattern, start_time=start, end_time=end)
    subject.is_working_day.cache_clear()


class TestExceptionTimes(test.bootstrap.IFC4):
    def test_removing_only_the_hours_of_an_exception_with_time_periods(self):
        calendar = add_calendar(self.file)
        thursday = MONDAY + datetime.timedelta(days=3)
        add_exception(self.file, calendar, thursday, [("13:00:00", "17:00:00")])
        assert subject.is_working_day(thursday, calendar) is True
        assert subject.get_work_periods(thursday, calendar) == [(9 * H, 13 * H)]

    def test_removing_the_day_for_an_exception_without_time_period(self):
        calendar = add_calendar(self.file)
        thursday = MONDAY + datetime.timedelta(days=3)
        add_exception(self.file, calendar, thursday)
        assert subject.is_working_day(thursday, calendar) is False
        assert subject.get_work_periods(thursday, calendar) == []


class TestGetWorkDayDuration(test.bootstrap.IFC4):
    def add_task(self, work_day_duration=None):
        if not self.file.by_type("IfcProject"):
            ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        if work_day_duration:
            pset = ifcopenshell.api.pset.add_pset(self.file, product=schedule, name="Pset_WorkControlCommon")
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"WorkDayDuration": work_day_duration})
        return ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule)

    def test_using_the_time_periods_of_the_calendar_first(self):
        task = self.add_task("PT8H")
        calendar = add_calendar(self.file, [("07:00:00", "12:00:00"), ("13:00:00", "17:00:00")])
        assert subject.get_work_day_duration(task, calendar) == 9 * H

    def test_using_the_work_day_duration_if_the_calendar_has_no_time_period(self):
        task = self.add_task("PT7H30M")
        assert subject.get_work_day_duration(task, add_calendar(self.file)) == 7.5 * H

    def test_using_8_hours_if_there_is_no_value(self):
        assert subject.get_work_day_duration(self.add_task()) == 8 * H

    def test_reading_a_work_day_duration_of_24_hours(self):
        assert subject.get_work_day_duration(self.add_task("PT24H")) == 24 * H


def at(day, hours, minutes=0):
    return datetime.datetime.combine(day, datetime.time(hours, minutes))


class TestOffsetDate(test.bootstrap.IFC4):
    def offset(self, start, duration, calendar=None, duration_type="WORKTIME"):
        return subject.offset_date(start, duration, duration_type, calendar)

    def test_offsetting_by_work_hours_in_the_same_day(self):
        assert self.offset(at(MONDAY, 9), 5 * H) == at(MONDAY, 14)

    def test_offsetting_by_work_hours_to_the_next_day(self):
        assert self.offset(at(MONDAY, 14), 5 * H) == at(MONDAY + datetime.timedelta(days=1), 11)

    def test_skipping_the_hours_between_time_periods(self):
        calendar = add_calendar(self.file, [("07:00:00", "12:00:00"), ("13:00:00", "17:00:00")])
        assert self.offset(at(MONDAY, 11), 2 * H, calendar) == at(MONDAY, 14)

    def test_skipping_the_days_without_work(self):
        calendar = add_calendar(self.file)
        friday = MONDAY + datetime.timedelta(days=4)
        assert self.offset(at(friday, 14), 5 * H, calendar) == at(MONDAY + datetime.timedelta(days=7), 11)

    def test_offsetting_back_by_work_hours(self):
        assert self.offset(at(MONDAY + datetime.timedelta(days=1), 11), -4 * H) == at(MONDAY, 15)

    def test_offsetting_by_work_days_and_hours(self):
        tuesday = MONDAY + datetime.timedelta(days=1)
        assert self.offset(at(MONDAY, 13), datetime.timedelta(days=1, hours=4)) == at(tuesday, 17)

    def test_offsetting_by_elapsed_hours(self):
        assert self.offset(at(MONDAY, 14), 5 * H, duration_type="ELAPSEDTIME") == at(MONDAY, 19)

    def test_offsetting_by_whole_days_as_before(self):
        assert self.offset(at(MONDAY, 9), datetime.timedelta(days=2)) == at(MONDAY + datetime.timedelta(days=2), 9)


class TestGetWorkStartAndFinish(test.bootstrap.IFC4):
    def test_moving_a_datetime_out_of_work_hours_to_the_next_start(self):
        assert subject.get_work_start(at(MONDAY, 17), None) == at(MONDAY + datetime.timedelta(days=1), 9)
        assert subject.get_work_start(at(MONDAY, 7), None) == at(MONDAY, 9)

    def test_moving_a_datetime_out_of_work_hours_to_the_previous_finish(self):
        assert subject.get_work_finish(at(MONDAY + datetime.timedelta(days=1), 9), None) == at(MONDAY, 17)

    def test_keeping_a_datetime_in_work_hours(self):
        assert subject.get_work_start(at(MONDAY, 13, 44), None) == at(MONDAY, 13, 44)
        assert subject.get_work_finish(at(MONDAY, 13, 44), None) == at(MONDAY, 13, 44)
