# This file was generated with the assistance of an AI coding tool.
# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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

import ifcopenshell.api.control
import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import ifcopenshell.util.resource
import ifcopenshell.util.sequence as subject
import test.bootstrap


class TestGetHoursInDay(test.bootstrap.IFC4):
    def add_calendar(self, *periods):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=work_time)
        for start_time, end_time in periods:
            ifcopenshell.api.sequence.add_time_period(
                self.file, recurrence_pattern=pattern, start_time=start_time, end_time=end_time
            )
        return calendar

    def test_no_calendar(self):
        assert subject.get_hours_in_day(None) is None

    def test_calendar_without_time_periods(self):
        assert subject.get_hours_in_day(self.add_calendar()) is None

    def test_periods_with_a_lunch_break(self):
        calendar = self.add_calendar(("09:00:00", "12:00:00"), ("13:00:00", "17:00:00"))
        assert subject.get_hours_in_day(calendar) == 7.0

    def test_overnight_period(self):
        assert subject.get_hours_in_day(self.add_calendar(("22:00:00", "06:00:00"))) == 8.0


class TestGetResourceCalendar(test.bootstrap.IFC4):
    def test_calendar_is_inherited_from_the_parent_resource(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        crew = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        labour = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource", parent_resource=crew)
        assert ifcopenshell.util.resource.get_calendar(labour) is None
        ifcopenshell.api.control.assign_control(self.file, relating_control=calendar, related_objects=[crew])
        assert ifcopenshell.util.resource.get_calendar(labour) == calendar
