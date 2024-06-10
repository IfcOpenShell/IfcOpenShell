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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.control
import ifcopenshell.api.sequence


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestRemoveWorkCalendar(test.bootstrap.IFC4):
    def test_remove_work_calendar(self):
        self.file.create_entity("IfcProject")
        work_calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)

        # Add work times.
        ifcopenshell.api.sequence.add_work_time(self.file, work_calendar, "WorkingTimes")
        ifcopenshell.api.sequence.add_work_time(self.file, work_calendar, "WorkingTimes")
        ifcopenshell.api.sequence.add_work_time(self.file, work_calendar, "ExceptionTimes")
        ifcopenshell.api.sequence.add_work_time(self.file, work_calendar, "ExceptionTimes")

        # Assign tasks.
        task = ifcopenshell.api.sequence.add_task(self.file)
        ifcopenshell.api.control.assign_control(self.file, work_calendar, task)

        ifcopenshell.api.sequence.remove_work_calendar(self.file, work_calendar)

        assert len(self.file.by_type("IfcWorkCalendar")) == 0
        assert len(self.file.by_type("IfcWorkTime")) == 0
        assert len(self.file.by_type("IfcTask")) == 1
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 0


class TestRemoveWorkCalendarIFC4X3(test.bootstrap.IFC4X3, TestRemoveWorkCalendar):
    pass
