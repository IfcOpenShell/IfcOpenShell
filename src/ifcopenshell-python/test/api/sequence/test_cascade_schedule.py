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

import datetime

import pytest

import ifcopenshell.api.control
import ifcopenshell.api.nest
import ifcopenshell.api.sequence
import test.bootstrap


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestCascadeSchedule(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_task_has_no_successors(self):
        task = ifcopenshell.api.sequence.add_task(self.file)
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime is None

    def test_not_affecting_tasks_that_are_not_related(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P1D")

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def test_moving_a_task_to_working_days_when_it_gains_a_calendar(self):
        task = self._create_task("P2D")
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-02T17:00:00"

        ifcopenshell.api.control.assign_control(
            self.file, relating_control=self._create_weekday_calendar(), related_objects=[task]
        )
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-04T17:00:00"

    def test_moving_nested_tasks_to_working_days_when_their_parent_gains_a_calendar(self):
        parent = ifcopenshell.api.sequence.add_task(self.file)
        task = self._create_task("P2D")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[task], relating_object=parent)

        ifcopenshell.api.control.assign_control(
            self.file, relating_control=self._create_weekday_calendar(), related_objects=[parent]
        )
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=parent)
        assert task.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-04T17:00:00"

    def test_counting_every_day_again_when_a_task_loses_its_calendar(self):
        calendar = self._create_weekday_calendar()
        task = ifcopenshell.api.sequence.add_task(self.file)
        ifcopenshell.api.control.assign_control(self.file, relating_control=calendar, related_objects=[task])
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            self.file,
            task_time=task_time,
            attributes={"ScheduleStart": datetime.date(1999, 12, 31), "ScheduleDuration": "P2D"},
        )
        assert task.TaskTime.ScheduleFinish == "2000-01-03T17:00:00"

        ifcopenshell.api.control.unassign_control(self.file, relating_control=calendar, related_objects=[task])
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "1999-12-31T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def test_keeping_the_span_of_a_task_without_a_duration_when_it_gains_a_calendar(self):
        task = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        task_time.ScheduleStart = "2000-01-01T09:00:00"
        task_time.ScheduleFinish = "2000-01-01T13:00:00"

        ifcopenshell.api.control.assign_control(
            self.file, relating_control=self._create_weekday_calendar(), related_objects=[task]
        )
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-03T13:00:00"

    def test_not_finishing_a_task_without_a_duration_on_a_non_working_day(self):
        task = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        task_time.ScheduleStart = "2000-01-01T09:00:00"
        task_time.ScheduleFinish = "2000-01-07T17:00:00"

        ifcopenshell.api.control.assign_control(
            self.file, relating_control=self._create_weekday_calendar(), related_objects=[task]
        )
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-03T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-10T17:00:00"

    def test_only_cascading_to_successors_not_predecessors(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task2)
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
            ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)

    def test_cascading_finish_to_start(self):
        task = self._create_task("P1D")
        task2 = self._create_task("P2D")
        task3 = self._create_task("P3D")
        self._create_sequence(task, task2, "FINISH_START")
        self._create_sequence(task, task3, "FINISH_START", lag="P1D")

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
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

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
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

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
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

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
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

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
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

        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        assert task.TaskTime.ScheduleStart == "2000-01-01T09:00:00"
        assert task.TaskTime.ScheduleFinish == "2000-01-01T09:00:00"
        assert task2.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task2.TaskTime.ScheduleFinish == "1999-12-31T17:00:00"
        assert task3.TaskTime.ScheduleStart == "1999-12-30T09:00:00"
        assert task3.TaskTime.ScheduleFinish == "2000-01-01T17:00:00"

    def _create_task(self, duration):
        task = ifcopenshell.api.sequence.add_task(self.file)
        if duration == "P0D":
            task.IsMilestone = True
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            self.file,
            task_time=task_time,
            attributes={"ScheduleStart": datetime.date(2000, 1, 1), "ScheduleDuration": duration},
        )
        return task

    def _create_weekday_calendar(self):
        self.file.create_entity("IfcProject")
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(
            self.file, parent=work_time, recurrence_type="WEEKLY"
        )
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file, recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]}
        )
        return calendar

    def _create_sequence(self, predecessor, successor, relationship, lag=None):
        rel = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )
        ifcopenshell.api.sequence.edit_sequence(self.file, rel_sequence=rel, attributes={"SequenceType": relationship})
        if lag:
            ifcopenshell.api.sequence.assign_lag_time(
                self.file, rel_sequence=rel, lag_value=lag, duration_type="WORKTIME"
            )
