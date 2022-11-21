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
import datetime
import test.bootstrap
import ifcopenshell.api


class TestCascadeSchedule(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_task_has_no_successors(self):
        task = ifcopenshell.api.run("sequence.add_task", self.file)
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime is None

    def test_not_affecting_tasks_that_are_not_related(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def test_only_cascading_to_successors_not_predecessors(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task2)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        # We assert that these start finish times have not cascaded
        assert task3.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-04T17:00:00"

    def test_catching_cyclic_relationships(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        self._create_sequence(task, task2, "FINISH_START")
        with pytest.raises(RecursionError):
            self._create_sequence(task2, task, "FINISH_START")
            ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)

    def test_cascading_finish_to_start(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        assert task3.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-05T17:00:00"

    def test_cascading_finish_to_start_for_milestones(self):
        task = self._create_task("P0D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-02T17:00:00"
        assert task3.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-04T17:00:00"

    def test_cascading_finish_to_finish(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_FINISH")
        self._create_sequence(task, task3, "FINISH_FINISH", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "1999-12-31T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task3.TaskTime.ScheduleStart == "1999-12-31T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-02T17:00:00"

    def test_cascading_start_to_start(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "START_START")
        self._create_sequence(task, task3, "START_START", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-02T17:00:00"
        assert task3.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-04T17:00:00"

    def test_cascading_start_to_finish(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "START_FINISH")
        self._create_sequence(task, task3, "START_FINISH", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "1999-12-31T17:00:00"
        assert task3.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def test_cascading_start_to_finish_for_milestones(self):
        task = self._create_task("P0D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "START_FINISH")
        self._create_sequence(task, task3, "START_FINISH", lag="P1D")

        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "1999-12-31T17:00:00"
        assert task3.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def _create_task(self, duration):
        task = ifcopenshell.api.run("sequence.add_task", self.file)
        if duration == "P0D":
            task.IsMilestone = True
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task)
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={"ScheduleStart": datetime.date(2000, 1, 1), "ScheduleDuration": duration},
        )
        return task

    def _create_sequence(self, predecessor, successor, relationship, lag=None):
        rel = ifcopenshell.api.run(
            "sequence.assign_sequence", self.file, relating_process=predecessor, related_process=successor
        )
        ifcopenshell.api.run(
            "sequence.edit_sequence", self.file, rel_sequence=rel, attributes={"SequenceType": relationship}
        )
        if lag:
            ifcopenshell.api.run(
                "sequence.assign_lag_time", self.file, rel_sequence=rel, lag_value=lag, duration_type="WORKTIME"
            )
