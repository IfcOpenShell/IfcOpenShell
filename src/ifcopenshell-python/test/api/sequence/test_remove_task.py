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
import ifcopenshell.api.nest
import ifcopenshell.api.sequence


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestRemoveTask(test.bootstrap.IFC4):
    def test_remove_task(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        ifcopenshell.api.sequence.remove_task(self.file, task)
        assert len(self.file.by_type("IfcTask")) == 0

    def test_remove_task_times(self):
        self.file.create_entity("IfcProject")

        task = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task, is_recurring=True)
        ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, task_time, recurrence_type="DAILY")

        task2 = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task2, is_recurring=False)

        ifcopenshell.api.sequence.remove_task(self.file, task)
        ifcopenshell.api.sequence.remove_task(self.file, task2)

        assert len(self.file.by_type("IfcTask")) == 0
        assert len(self.file.by_type("IfcTaskTime")) == 0
        assert len(self.file.by_type("IfcRecurrencePattern")) == 0

    def test_remove_task_with_subtasks(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        subtask1 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        subtask2 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subtask1, subtask2], relating_object=task)
        ifcopenshell.api.sequence.remove_task(self.file, task)
        assert len(self.file.by_type("IfcTask")) == 0
        assert len(self.file.by_type("IfcRelNests")) == 0

    def test_remove_subtask(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        subtask1 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subtask1], relating_object=task)
        ifcopenshell.api.sequence.remove_task(self.file, subtask1)
        assert len(self.file.by_type("IfcTask")) == 1
        assert len(self.file.by_type("IfcRelNests")) == 0


class TestRemoveTaskIFC4X3(test.bootstrap.IFC4X3, TestRemoveTask):
    pass
