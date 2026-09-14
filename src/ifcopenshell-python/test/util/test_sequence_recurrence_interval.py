# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

import test.bootstrap
import ifcopenshell.util.sequence as subject


class TestIsWorkTimeApplicableToDayRecurrenceInterval(test.bootstrap.IFC4):
    # All Interval/Occurrences tests anchor Start one cycle before the day
    # under test. IfcWorkTime's own Start day is separately excluded by
    # is_day_in_work_time's strict `>` check (a pre-existing, unrelated
    # issue), so asserting on the Start day itself would conflate the two.

    def test_daily_interval_matches_every_other_day_not_the_days_between(self):
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="DAILY", Interval=2)
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 2)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 3)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 4)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 5)) is True

    def test_daily_neither_interval_nor_occurrences_matches_every_day(self):
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="DAILY")
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 2)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 3)) is True

    def test_daily_occurrences_stops_matching_after_the_right_number(self):
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="DAILY", Occurrences=3)
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 2)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 3)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 4)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 5)) is False

    def test_weekly_interval_matches_every_other_saturday_not_the_saturday_between(self):
        # Docstring's WEEKLY example: "every other saturday".
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern", RecurrenceType="WEEKLY", WeekdayComponent=[6], Interval=2
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-06-27")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 4)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 11)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 18)) is False

    def test_weekly_neither_interval_nor_occurrences_matches_every_saturday(self):
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="WEEKLY", WeekdayComponent=[6])
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-06-27")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 4)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 11)) is True

    def test_monthly_by_day_of_month_interval_matches_docstring_example(self):
        # The maintenance task must occur every 6 months, on the 1st.
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern", RecurrenceType="MONTHLY_BY_DAY_OF_MONTH", DayComponent=[1], Interval=6
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 3, 1)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 1)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2027, 1, 1)) is True

    def test_monthly_by_day_of_month_neither_set_matches_every_month(self):
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern", RecurrenceType="MONTHLY_BY_DAY_OF_MONTH", DayComponent=[1]
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 3, 1)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 1)) is True

    def test_monthly_by_position_interval_matches_every_other_month(self):
        # Second Tuesday of every other month.
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern",
            RecurrenceType="MONTHLY_BY_POSITION",
            WeekdayComponent=[2],
            Position=2,
            Interval=2,
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 13)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 2, 10)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 3, 10)) is True

    def test_yearly_by_day_of_month_interval_matches_every_other_year(self):
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern",
            RecurrenceType="YEARLY_BY_DAY_OF_MONTH",
            DayComponent=[25],
            MonthComponent=[12],
            Interval=2,
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 12, 25)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2027, 12, 25)) is False
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2028, 12, 25)) is True

    def test_yearly_by_day_of_month_neither_set_matches_every_year(self):
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern", RecurrenceType="YEARLY_BY_DAY_OF_MONTH", DayComponent=[25], MonthComponent=[12]
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 12, 25)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2027, 12, 25)) is True

    def test_yearly_by_position_occurrences_stops_matching_after_the_right_number(self):
        # Third Wednesday of January, for 2 occurrences.
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern",
            RecurrenceType="YEARLY_BY_POSITION",
            WeekdayComponent=[3],
            Position=3,
            MonthComponent=[1],
            Occurrences=2,
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 14)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2027, 1, 20)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2028, 1, 19)) is False

    def test_yearly_by_position_neither_set_matches_every_year(self):
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern",
            RecurrenceType="YEARLY_BY_POSITION",
            WeekdayComponent=[3],
            Position=3,
            MonthComponent=[1],
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence, Start="2026-01-01")
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 14)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2027, 1, 20)) is True

    def test_interval_without_start_returns_false_instead_of_faking_an_anchor(self):
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="DAILY", Interval=2)
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence)
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 1, 2)) is False

    def test_occurrences_without_start_returns_false_instead_of_faking_an_anchor(self):
        recurrence = self.file.create_entity(
            "IfcRecurrencePattern", RecurrenceType="MONTHLY_BY_DAY_OF_MONTH", DayComponent=[1], Occurrences=3
        )
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence)
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 3, 1)) is False
