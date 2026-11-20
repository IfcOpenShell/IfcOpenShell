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
import ifcopenshell.util.date
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

    def test_reading_an_end_time_of_24_00_as_the_end_of_the_day(self):
        calendar = add_calendar(self.file, [("16:00:00", "24:00:00")])
        assert self.file.by_type("IfcTimePeriod")[0].EndTime == "24:00:00"
        assert subject.get_work_periods(MONDAY, calendar) == [(16 * H, 24 * H)]
        assert subject.get_work_day_duration(None, calendar) == 8 * H

    def test_returning_no_period_on_a_day_without_work(self):
        calendar = add_calendar(self.file, [("07:00:00", "12:00:00")])
        assert subject.get_work_periods(SATURDAY, calendar) == []


def add_exception(file, calendar, day, periods=None):
    work_time = ifcopenshell.api.sequence.add_work_time(file, work_calendar=calendar, time_type="ExceptionTimes")
    ifcopenshell.api.sequence.edit_work_time(
        file, work_time=work_time, attributes={"Start": day.isoformat(), "Finish": day.isoformat()}
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

    def test_including_the_start_and_finish_dates_of_an_exception(self):
        calendar = add_calendar(self.file)
        tuesday, wednesday = (MONDAY + datetime.timedelta(days=i) for i in (1, 2))
        work_time = ifcopenshell.api.sequence.add_work_time(
            self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        ifcopenshell.api.sequence.edit_work_time(
            self.file, work_time=work_time, attributes={"Start": tuesday.isoformat(), "Finish": wednesday.isoformat()}
        )
        days = [MONDAY + datetime.timedelta(days=i) for i in range(4)]
        assert [subject.is_working_day(day, calendar) for day in days] == [True, False, False, True]

    def test_using_the_working_days_after_a_calendar_edit(self):
        calendar = add_calendar(self.file)
        thursday = MONDAY + datetime.timedelta(days=3)
        assert subject.is_working_day(thursday, calendar) is True
        work_time = ifcopenshell.api.sequence.add_work_time(
            self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        ifcopenshell.api.sequence.edit_work_time(
            self.file, work_time=work_time, attributes={"Start": thursday.isoformat(), "Finish": thursday.isoformat()}
        )
        assert subject.is_working_day(thursday, calendar) is False
        ifcopenshell.api.sequence.remove_work_time(self.file, work_time=work_time)
        assert subject.is_working_day(thursday, calendar) is True


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
        assert self.offset(at(MONDAY, 9), datetime.timedelta(days=1, hours=4)) == at(tuesday, 13)

    def test_offsetting_by_elapsed_hours(self):
        assert self.offset(at(MONDAY, 14), 5 * H, duration_type="ELAPSEDTIME") == at(MONDAY, 19)

    def test_offsetting_by_whole_days_as_before(self):
        assert self.offset(at(MONDAY, 9), datetime.timedelta(days=2)) == at(MONDAY + datetime.timedelta(days=2), 9)

    def test_keeping_the_side_of_a_break_when_offsetting_by_work_days(self):
        calendar = add_calendar(self.file, [("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")])
        tuesday = MONDAY + datetime.timedelta(days=1)
        # 12:00 and 13:00 are the same work instant, but not for a task in other work periods.
        assert subject.offset_work_days(at(MONDAY, 13), 1, calendar) == at(tuesday, 13)
        assert subject.offset_work_days(at(MONDAY, 12), 1, calendar) == at(tuesday, 12)
        assert subject.offset_work_days(at(tuesday, 13), -1, calendar) == at(MONDAY, 13)
        assert subject.offset_work_days(at(tuesday, 12), -1, calendar) == at(MONDAY, 12)

    def test_offsetting_by_calendar_months_and_years(self):
        month, year = (ifcopenshell.util.date.parse_duration(d) for d in ("P1M", "P1Y"))
        start = at(datetime.date(2026, 1, 31), 9)
        assert self.offset(start, month, duration_type="ELAPSEDTIME") == at(datetime.date(2026, 2, 28), 9)
        assert self.offset(at(datetime.date(2026, 2, 1), 9), month, duration_type="ELAPSEDTIME") == at(
            datetime.date(2026, 3, 1), 9
        )
        assert self.offset(start, year, duration_type="ELAPSEDTIME") == at(datetime.date(2027, 1, 31), 9)


class TestGetWorkStartAndFinish(test.bootstrap.IFC4):
    def test_moving_a_datetime_out_of_work_hours_to_the_next_start(self):
        assert subject.get_work_start(at(MONDAY, 17), None) == at(MONDAY + datetime.timedelta(days=1), 9)
        assert subject.get_work_start(at(MONDAY, 7), None) == at(MONDAY, 9)

    def test_moving_a_datetime_out_of_work_hours_to_the_previous_finish(self):
        assert subject.get_work_finish(at(MONDAY + datetime.timedelta(days=1), 9), None) == at(MONDAY, 17)

    def test_keeping_a_datetime_in_work_hours(self):
        assert subject.get_work_start(at(MONDAY, 13, 44), None) == at(MONDAY, 13, 44)
        assert subject.get_work_finish(at(MONDAY, 13, 44), None) == at(MONDAY, 13, 44)


class TestGetStartOrFinishDate(test.bootstrap.IFC4):
    def test_adding_elapsed_days_as_24_hours(self):
        calendar = add_calendar(self.file)
        finish = subject.get_start_or_finish_date(at(MONDAY, 9), datetime.timedelta(days=1), "ELAPSEDTIME", calendar)
        assert finish == at(MONDAY + datetime.timedelta(days=1), 9)

    def test_finishing_a_work_day_at_the_end_of_the_work_period(self):
        finish = subject.get_start_or_finish_date(at(MONDAY, 9), datetime.timedelta(days=1), "WORKTIME", None)
        assert finish == at(MONDAY, 17)
        start = subject.get_start_or_finish_date(at(MONDAY, 17), datetime.timedelta(days=1), "WORKTIME", None, "START")
        assert start == at(MONDAY, 9)


class TestGetWorkTime(test.bootstrap.IFC4):
    def test_summing_the_work_periods_between_two_datetimes(self):
        calendar = add_calendar(self.file, [("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")])
        assert subject.get_work_time(at(MONDAY, 11), at(MONDAY, 14), calendar) == 2 * H

    def test_skipping_the_days_without_work(self):
        calendar = add_calendar(self.file, [("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")])
        assert (
            subject.get_work_time(
                at(MONDAY + datetime.timedelta(days=4), 16), at(MONDAY + datetime.timedelta(days=7), 9), calendar
            )
            == 2 * H
        )

    def test_returning_a_negative_work_time_for_a_finish_before_the_start(self):
        assert subject.get_work_time(at(MONDAY, 14), at(MONDAY, 11), None) == -3 * H

    def test_returning_no_work_time_for_the_same_work_instant(self):
        assert subject.get_work_time(at(MONDAY, 17), at(MONDAY + datetime.timedelta(days=1), 9), None) == 0 * H


class TestOffsetLag(test.bootstrap.IFC4):
    def setup_calendar(self):
        return add_calendar(self.file, [("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")])

    def test_offsetting_by_a_lag_in_work_time(self):
        calendar = self.setup_calendar()
        assert subject.offset_lag(at(MONDAY + datetime.timedelta(days=4), 16), 2 * H, "WORKTIME", calendar) == at(
            MONDAY + datetime.timedelta(days=7), 9
        )

    def test_offsetting_by_a_lag_in_elapsed_time(self):
        calendar = self.setup_calendar()
        assert subject.offset_lag(at(MONDAY + datetime.timedelta(days=4), 17), 16 * H, "ELAPSEDTIME", calendar) == at(
            SATURDAY, 9
        )

    def test_giving_the_earliest_work_instant_forward_for_a_negative_lag(self):
        calendar = self.setup_calendar()
        assert subject.offset_lag(at(MONDAY + datetime.timedelta(days=7), 10), -2 * H, "WORKTIME", calendar) == at(
            MONDAY + datetime.timedelta(days=4), 17
        )

    def test_giving_the_latest_work_instant_backward_for_a_negative_lag(self):
        calendar = self.setup_calendar()
        result = subject.offset_lag(
            at(MONDAY + datetime.timedelta(days=4), 15), -2 * H, "WORKTIME", calendar, is_forward=False
        )
        assert result == at(MONDAY + datetime.timedelta(days=7), 8)

    def test_keeping_the_date_for_no_lag(self):
        assert subject.offset_lag(at(SATURDAY, 10), datetime.timedelta(), "WORKTIME", None) == at(SATURDAY, 10)


class TestSnapDate(test.bootstrap.IFC4):
    def setup_calendar(self):
        return add_calendar(self.file, [("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")])

    def test_moving_a_start_to_the_next_work_period(self):
        calendar = self.setup_calendar()
        assert subject.snap_date(at(SATURDAY, 10), "START", calendar) == at(MONDAY + datetime.timedelta(days=7), 8)

    def test_moving_a_finish_to_the_previous_work_period(self):
        calendar = self.setup_calendar()
        assert subject.snap_date(at(SATURDAY, 10), "FINISH", calendar) == at(MONDAY + datetime.timedelta(days=4), 17)


class TestGetWorkDuration:
    def test_converting_work_hours_of_one_work_day_or_more_to_work_days(self):
        assert subject.get_work_duration("PT24H", "WORKTIME") == datetime.timedelta(days=3)
        assert subject.get_work_duration("PT18H", "WORKTIME", 9 * H) == datetime.timedelta(days=2)

    def test_reading_work_days_and_work_hours(self):
        assert subject.get_work_duration("P1DT12H", "WORKTIME") == datetime.timedelta(days=2, hours=4)
        assert subject.get_work_duration("PT5H", "WORKTIME") == 5 * H
        assert subject.get_work_duration("P2D", "WORKTIME") == datetime.timedelta(days=2)

    def test_reading_a_negative_work_duration(self):
        assert subject.get_work_duration("-PT4H", "WORKTIME") == -4 * H

    def test_reading_an_elapsed_duration_as_it_is(self):
        assert subject.get_work_duration("PT24H", "ELAPSEDTIME") == datetime.timedelta(days=1)


def add_short_friday_calendar(file):
    # Monday to Thursday from 09:00 to 17:00 (8 hours), Friday from 09:00 to 15:00 (6 hours)
    calendar = add_calendar(file, [("09:00:00", "17:00:00")], weekdays=(1, 2, 3, 4))
    work_time = ifcopenshell.api.sequence.add_work_time(file, work_calendar=calendar)
    pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(file, parent=work_time, recurrence_type="WEEKLY")
    ifcopenshell.api.sequence.edit_recurrence_pattern(
        file, recurrence_pattern=pattern, attributes={"WeekdayComponent": [5]}
    )
    ifcopenshell.api.sequence.add_time_period(file, recurrence_pattern=pattern, start_time="09:00", end_time="15:00")
    return calendar


THURSDAY = MONDAY + datetime.timedelta(days=3)
FRIDAY = MONDAY + datetime.timedelta(days=4)
NEXT_MONDAY = MONDAY + datetime.timedelta(days=7)


class TestWorkDaysOfDifferentLengths(test.bootstrap.IFC4):
    def finish(self, start, duration):
        return subject.get_start_or_finish_date(start, duration, "WORKTIME", self.calendar, "FINISH")

    def start(self, finish, duration):
        return subject.get_start_or_finish_date(finish, duration, "WORKTIME", self.calendar, "START")

    def setup_calendar(self):
        self.calendar = add_short_friday_calendar(self.file)

    def test_counting_each_working_day_as_one_work_day(self):
        self.setup_calendar()
        assert self.finish(at(FRIDAY, 9), "P1D") == at(FRIDAY, 15)
        assert self.finish(at(THURSDAY, 9), "P2D") == at(FRIDAY, 15)
        assert self.finish(at(THURSDAY, 9), "P3D") == at(NEXT_MONDAY, 17)
        assert self.start(at(FRIDAY, 15), "P2D") == at(THURSDAY, 9)

    def test_counting_a_part_of_a_day_as_a_full_day(self):
        self.setup_calendar()
        # A part of Thursday has no length that Thursday and Friday share: the task takes all of Friday.
        assert self.finish(at(THURSDAY, 13), "P1D") == at(FRIDAY, 15)
        assert self.finish(at(THURSDAY, 16), "P1D") == at(FRIDAY, 15)
        # Backward, the latest start that finishes at or before Friday 12:00 is the start of Thursday.
        assert self.start(at(FRIDAY, 12), "P1D") == at(THURSDAY, 9)
        assert self.start(at(FRIDAY, 15), "P1D") == at(FRIDAY, 9)

    def test_offsetting_an_instant_to_the_same_position_in_the_next_day(self):
        self.setup_calendar()
        # A lag moves an instant: 13:00 is half of Thursday, and half of Friday is 12:00. A negative offset reverses
        # a positive offset. The task after the lag starts at the start of a day (see snap_task_date).
        assert subject.offset_work_days(at(THURSDAY, 13), 1, self.calendar) == at(FRIDAY, 12)
        assert subject.offset_work_days(at(THURSDAY, 16), 1, self.calendar) == at(FRIDAY, 14, 15)
        assert subject.offset_work_days(at(FRIDAY, 12), -1, self.calendar) == at(THURSDAY, 13)
        assert subject.offset_work_days(at(THURSDAY, 13), 0.5, self.calendar) == at(FRIDAY, 9)

    def test_moving_a_task_of_work_days_to_whole_days(self):
        self.setup_calendar()
        snap = subject.snap_task_date
        days, hours = (subject.get_work_duration(d, "WORKTIME") for d in ("P1D", "PT4H"))
        assert snap(at(THURSDAY, 13), "START", days, "WORKTIME", self.calendar) == at(FRIDAY, 9)
        assert snap(at(THURSDAY, 13), "FINISH", days, "WORKTIME", self.calendar) == at(THURSDAY, 17)
        assert snap(at(THURSDAY, 13), "START", days, "WORKTIME", self.calendar, is_forward=False) == at(THURSDAY, 9)
        assert snap(at(FRIDAY, 12), "FINISH", days, "WORKTIME", self.calendar, is_forward=False) == at(THURSDAY, 17)
        assert snap(at(THURSDAY, 9), "START", days, "WORKTIME", self.calendar) == at(THURSDAY, 9)
        # Work hours are exact, and elapsed time does not use the work periods.
        assert snap(at(THURSDAY, 13), "START", hours, "WORKTIME", self.calendar) == at(THURSDAY, 13)
        mixed = subject.get_work_duration("P1DT4H", "WORKTIME")
        assert snap(at(THURSDAY, 13), "START", mixed, "WORKTIME", self.calendar) == at(FRIDAY, 9)
        assert snap(at(FRIDAY, 12), "FINISH", mixed, "WORKTIME", self.calendar) == at(FRIDAY, 12)
        assert snap(at(THURSDAY, 13), "START", days, "ELAPSEDTIME", self.calendar) == at(THURSDAY, 13)

    def test_getting_the_dates_of_a_task_from_a_limit_of_its_finish(self):
        self.setup_calendar()
        get = subject.get_task_dates_from_finish
        days, mixed, hours = (subject.get_work_duration(d, "WORKTIME") for d in ("P1D", "P1DT4H", "PT4H"))
        wednesday = MONDAY + datetime.timedelta(days=2)
        # A finish at or after Friday 12:00: one work day takes all of Friday.
        assert get(at(FRIDAY, 12), days, "WORKTIME", self.calendar) == (at(FRIDAY, 9), at(FRIDAY, 15))
        # A finish at or before Friday 12:00: all of Thursday.
        assert get(at(FRIDAY, 12), days, "WORKTIME", self.calendar, is_forward=False) == (
            at(THURSDAY, 9),
            at(THURSDAY, 17),
        )
        # A work day from the start of a day, then 4 work hours.
        assert get(at(FRIDAY, 12), mixed, "WORKTIME", self.calendar) == (at(THURSDAY, 9), at(FRIDAY, 13))
        assert get(at(FRIDAY, 12), mixed, "WORKTIME", self.calendar, is_forward=False) == (
            at(wednesday, 9),
            at(THURSDAY, 13),
        )
        # Work hours only: exact.
        assert get(at(FRIDAY, 12), hours, "WORKTIME", self.calendar) == (at(THURSDAY, 16), at(FRIDAY, 12))

    def test_offsetting_work_hours_through_the_days(self):
        self.setup_calendar()
        assert self.finish(at(FRIDAY, 9), "PT10H") == at(NEXT_MONDAY, 13)
        assert self.finish(at(THURSDAY, 13), "PT10H") == at(FRIDAY, 15)
        # All of Friday, then 4 work hours
        assert self.finish(at(THURSDAY, 13), "P1DT4H") == at(NEXT_MONDAY, 13)

    def test_never_finishing_earlier_after_a_later_start(self):
        self.setup_calendar()
        starts = [at(THURSDAY, 9) + i * datetime.timedelta(minutes=30) for i in range(5 * 48)]
        for duration in ("P1D", "P2DT3H", "PT10H"):
            finishes = [self.finish(start, duration) for start in starts]
            assert finishes == sorted(finishes)

    def test_reversing_an_offset(self):
        self.setup_calendar()
        starts = [at(THURSDAY, 9) + i * datetime.timedelta(minutes=45) for i in range(3 * 32)]
        for duration in ("P1D", "P2DT3H", "PT10H", "P1DT30M"):
            for start in starts:
                start = subject.get_work_start(start, self.calendar)
                finish = self.finish(start, duration)
                # A task of work days starts at the start of a working day.
                start = subject.snap_task_date(start, "START", duration, "WORKTIME", self.calendar)
                assert not subject.get_work_time(self.start(finish, duration), start, self.calendar)

    def test_counting_a_day_with_a_partial_exception_as_one_work_day(self):
        self.setup_calendar()
        wednesday = MONDAY + datetime.timedelta(days=2)
        add_exception(self.file, self.calendar, wednesday, [("13:00:00", "17:00:00")])
        assert self.finish(at(wednesday, 9), "P1D") == at(wednesday, 13)

    def test_getting_the_work_days_and_work_time_between_two_dates(self):
        self.setup_calendar()
        between = subject.get_work_duration_between
        assert between(at(THURSDAY, 9), at(FRIDAY, 15), self.calendar) == "P2D"
        assert between(at(THURSDAY, 9), at(NEXT_MONDAY, 11), self.calendar) == "P2DT2H"
        # Work days are exact only from the start of a day. From another time: work hours only.
        assert between(at(THURSDAY, 13), at(NEXT_MONDAY, 13), self.calendar) == "PT14H"
        assert between(at(THURSDAY, 13), at(FRIDAY, 14), self.calendar) == "PT9H"
        assert between(at(FRIDAY, 14), at(THURSDAY, 13), self.calendar) == "-PT9H"
        for start in (at(THURSDAY, 9), at(THURSDAY, 10), at(THURSDAY, 16), at(FRIDAY, 13)):
            finish = at(NEXT_MONDAY, 11)
            duration = between(start, finish, self.calendar)
            assert subject.offset_date(start, duration, "WORKTIME", self.calendar) == finish
