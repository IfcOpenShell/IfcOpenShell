# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.sequence
import ifcopenshell.util.sequence
import test.bootstrap


class TestCopyWorkSchedule(test.bootstrap.IFC4):
    def test_run(self):
        self.file.create_entity("IfcProject")
        # Shared code logic with test_copy_cost_schedule.
        work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, work_plan=work_plan)
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule)
        ifcopenshell.api.sequence.add_task(self.file, parent_task=task)  # Subtask.
        old_cost_items = set(self.file.by_type("IfcTask"))

        new_schedule = ifcopenshell.api.sequence.copy_work_schedule(self.file, schedule)

        # We don't check how well IfcTasks are copied,
        # it should be tested separately in test_duplicate_task.
        assert isinstance(new_schedule, ifcopenshell.entity_instance)
        assert new_schedule != schedule
        assert len(ifcopenshell.util.sequence.get_root_tasks(new_schedule)) == 1
        new_tasks = set(ifcopenshell.util.sequence.get_work_schedule_tasks(new_schedule))
        assert len(new_tasks) == 2
        assert len(new_tasks.intersection(old_cost_items)) == 0


class TestCopyWorkScheduleIFC2X3(test.bootstrap.IFC2X3, TestCopyWorkSchedule):
    pass


class TestCopyWorkScheduleIFC4X3(test.bootstrap.IFC4X3, TestCopyWorkSchedule):
    pass
