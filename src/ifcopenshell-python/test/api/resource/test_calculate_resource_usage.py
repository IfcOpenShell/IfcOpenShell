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

import ifcopenshell.api.control
import ifcopenshell.api.pset
import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import test.bootstrap


class TestCalculateResourceUsage(test.bootstrap.IFC4):
    def add_resource(self, work_day_duration=None, time_periods=()):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        if work_day_duration:
            pset = ifcopenshell.api.pset.add_pset(self.file, product=schedule, name="Pset_WorkControlCommon")
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"WorkDayDuration": work_day_duration})
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        task_time.ScheduleDuration = "P1D"
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        resource_time.ScheduleWork = "PT18H"
        ifcopenshell.api.sequence.assign_process(self.file, relating_process=task, related_object=resource)
        if time_periods:
            calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
            work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
            pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=work_time)
            for start, end in time_periods:
                ifcopenshell.api.sequence.add_time_period(
                    self.file, recurrence_pattern=pattern, start_time=start, end_time=end
                )
            ifcopenshell.api.control.assign_control(self.file, relating_control=calendar, related_objects=[resource])
        return resource

    def test_using_8_hours_for_a_work_day(self):
        resource = self.add_resource()
        ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
        assert resource.Usage.ScheduleUsage == 2.25

    def test_using_the_work_day_duration_of_the_work_schedule(self):
        resource = self.add_resource(work_day_duration="PT9H")
        ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
        assert resource.Usage.ScheduleUsage == 2.0

    def test_using_the_time_periods_of_the_resource_calendar(self):
        resource = self.add_resource(time_periods=(("07:00:00", "12:00:00"), ("13:00:00", "17:00:00")))
        ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
        assert resource.Usage.ScheduleUsage == 2.0
