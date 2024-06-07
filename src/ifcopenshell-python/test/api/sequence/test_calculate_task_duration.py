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

import test.bootstrap
import ifcopenshell.api


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestCalculateTaskDuration(test.bootstrap.IFC4):
    def test_calculating_the_duration_based_on_a_labour_resource_with_work_hours(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P6D"

    def test_calculating_the_duration_based_on_a_labour_resource_with_work_days(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "P3.5D"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P4D"

    def test_calculating_a_task_duration_without_a_work_schedule_defining_workday_duration(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        task = ifcopenshell.api.run("sequence.add_task", self.file)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "P2D"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P2D"

    def test_calculating_a_task_duration_with_a_custom_workday_duration(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=schedule, name="Pset_WorkControlCommon")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"WorkDayDuration": "PT2H"})
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P24D"

    def test_failing_to_calculate_if_no_schedule_work_usage(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime is None

    def test_calculating_a_nested_task_duration_based_on_a_labour_resource_with_work_hours(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        subtask = ifcopenshell.api.run("sequence.add_task", self.file, parent_task=task)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=subtask, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=subtask)
        assert subtask.TaskTime.ScheduleDuration == "P6D"
