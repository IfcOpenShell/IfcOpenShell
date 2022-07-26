# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


# A good way for checking these is to recreate them in ProjectLibre
class TestRecalculateSchedule(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_task_has_no_time(self):
        self._add_work_schedule()
        task = ifcopenshell.api.run("sequence.add_task", self.file)
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime is None

    def test_catching_cyclic_relationships(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P2D")
        task4 = self._create_task("P2D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task4, "FINISH_START")
        self._create_sequence(task2, task3, "FINISH_START")
        with pytest.raises(RecursionError):
            self._create_sequence(task3, task2, "FINISH_START")
        with pytest.raises(RecursionError):
            ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)

    def test_recalculating_for_a_single_task(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True

    def test_recalculating_finish_to_start(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        self._create_sequence(task, task2, "FINISH_START")
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.LateStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True

    def test_recalculating_multiple_finish_to_start(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.LateStart == "2000-01-04T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-05T17:00:00"
        assert task2.TaskTime.TotalFloat == "P2D"
        assert task2.TaskTime.FreeFloat == "P2D"
        assert task2.TaskTime.IsCritical is False
        assert task3.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-05T17:00:00"
        assert task3.TaskTime.EarlyStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.EarlyFinish == "2000-01-05T17:00:00"
        assert task3.TaskTime.LateStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.LateFinish == "2000-01-05T17:00:00"
        assert task3.TaskTime.TotalFloat == "P0D"
        assert task3.TaskTime.FreeFloat == "P0D"
        assert task3.TaskTime.IsCritical is True

    def test_recalculating_finish_to_start_with_a_milestone(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P0D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.LateStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True
        assert task3.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-03T09:00:00"
        assert task3.TaskTime.EarlyStart == "2000-01-03T09:00:00"
        assert task3.TaskTime.EarlyFinish == "2000-01-03T09:00:00"
        assert task3.TaskTime.LateStart == "2000-01-03T17:00:00"
        assert task3.TaskTime.LateFinish == "2000-01-03T17:00:00"
        assert task3.TaskTime.TotalFloat == "P1D"
        assert task3.TaskTime.FreeFloat == "P1D"
        assert task3.TaskTime.IsCritical is False

    def test_recalculating_finish_to_start_with_a_milestone_as_the_last_task(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P0D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task2, task3, "FINISH_START")
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.LateStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-03T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True
        assert task3.TaskTime.ScheduleStart == "2000-01-04T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-04T09:00:00"
        assert task3.TaskTime.EarlyStart == "2000-01-04T09:00:00"
        assert task3.TaskTime.EarlyFinish == "2000-01-04T09:00:00"
        assert task3.TaskTime.LateStart == "2000-01-04T09:00:00"
        assert task3.TaskTime.LateFinish == "2000-01-04T09:00:00"
        assert task3.TaskTime.TotalFloat == "P0D"
        assert task3.TaskTime.FreeFloat == "P0D"
        assert task3.TaskTime.IsCritical is True

    def test_recalculating_finish_to_finish(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        self._create_sequence(task, task2, "FINISH_FINISH")
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "1999-12-31T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.EarlyStart == "1999-12-31T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.LateStart == "1999-12-31T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True

    def test_recalculating_start_to_start(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        self._create_sequence(task, task2, "START_START")
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-02T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-02T17:00:00"
        assert task2.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-02T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True

    def test_recalculating_start_to_finish(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        self._create_sequence(task, task2, "START_FINISH")
        ifcopenshell.api.run("sequence.recalculate_schedule", self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.LateStart == "2000-01-01T09:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task.TaskTime.TotalFloat == "P0D"
        assert task.TaskTime.FreeFloat == "P0D"
        assert task.TaskTime.IsCritical is True
        assert task2.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "1999-12-31T17:00:00"
        assert task2.TaskTime.EarlyStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.EarlyFinish == "1999-12-31T17:00:00"
        assert task2.TaskTime.LateStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.LateFinish == "1999-12-31T17:00:00"
        assert task2.TaskTime.TotalFloat == "P0D"
        assert task2.TaskTime.FreeFloat == "P0D"
        assert task2.TaskTime.IsCritical is True

    def _add_work_schedule(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        self.work_schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)

    def _create_task(self, duration):
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=self.work_schedule)
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
