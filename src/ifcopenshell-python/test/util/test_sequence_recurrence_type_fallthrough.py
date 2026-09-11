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


class TestIsWorkTimeApplicableToDay(test.bootstrap.IFC4):
    def test_unhandled_recurrence_types_return_a_real_bool_not_none(self):
        # BY_DAY_COUNT and BY_WEEKDAY_COUNT are valid IfcRecurrenceTypeEnum
        # members (see RECURRENCE_TYPE) but have no interval-based
        # implementation yet. The function is annotated -> bool and every
        # other unimplemented case in it explicitly returns False; these two
        # must not be the only ones falling through to an implicit None.
        work_time = self.file.create_entity("IfcWorkTime")
        for recurrence_type in ("BY_DAY_COUNT", "BY_WEEKDAY_COUNT"):
            recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType=recurrence_type)
            work_time.RecurrencePattern = recurrence
            result = subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 30))
            assert result is False, f"{recurrence_type} returned {result!r}, expected the explicit bool False"

    def test_every_recurrence_type_survives_absent_optional_components(self):
        # Only RecurrenceType is mandatory on IfcRecurrencePattern; DayComponent,
        # WeekdayComponent, MonthComponent and Position are all optional, so a
        # pattern carrying none of them is valid IFC and must not raise.
        work_time = self.file.create_entity("IfcWorkTime")
        for recurrence_type in subject.RECURRENCE_TYPE.__args__:
            recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType=recurrence_type)
            work_time.RecurrencePattern = recurrence
            result = subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 30))
            assert isinstance(result, bool), f"{recurrence_type} returned {result!r}, expected a bool"

    def test_a_populated_weekday_component_still_decides_the_day(self):
        # Guarding the absent case must not neuter the populated one.
        recurrence = self.file.create_entity("IfcRecurrencePattern", RecurrenceType="WEEKLY", WeekdayComponent=[4])
        work_time = self.file.create_entity("IfcWorkTime", RecurrencePattern=recurrence)
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 30)) is True
        assert subject.is_work_time_applicable_to_day(work_time, datetime.date(2026, 7, 31)) is False
