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
class TestUnassignRecurrencePattern(test.bootstrap.IFC4):
    def test_unassigning_a_recurrence_pattern_updates_calculated_working_days(self):
        self.file.create_entity("IfcProject")
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=work_time)
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file, recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]}
        )
        start = datetime.date(2020, 1, 1)
        finish = datetime.date(2020, 1, 14)
        assert ifcopenshell.util.sequence.count_working_days(start, finish, calendar) == 10

        ifcopenshell.api.sequence.unassign_recurrence_pattern(self.file, recurrence_pattern=pattern)
        assert ifcopenshell.util.sequence.count_working_days(start, finish, calendar) == 14


class TestUnassignRecurrencePatternIFC4X3(test.bootstrap.IFC4X3, TestUnassignRecurrencePattern):
    pass
