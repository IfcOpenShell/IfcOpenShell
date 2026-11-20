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

import datetime

import pytest

import ifcopenshell.api.control
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import test.bootstrap


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
# A good way for checking these is to recreate them in ProjectLibre
class TestRecalculateSchedule(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_task_has_no_time(self):
        self._add_work_schedule()
        task = ifcopenshell.api.sequence.add_task(self.file)
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
            ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)

    def test_recalculating_a_float_over_a_weekend_in_work_time(self):
        self._add_work_schedule()
        calendar = ifcopenshell.api.sequence.add_work_calendar(self.file)
        work_time = ifcopenshell.api.sequence.add_work_time(self.file, work_calendar=calendar)
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(self.file, parent=work_time)
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file, recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]}
        )
        ifcopenshell.api.sequence.add_time_period(
            self.file, recurrence_pattern=pattern, start_time="09:00:00", end_time="17:00:00"
        )
        friday = datetime.date(2026, 1, 9)
        task = self._create_task("P1DT2H", start=friday, calendar=calendar)
        task2 = self._create_task("PT6H", start=friday, calendar=calendar)
        task3 = self._create_task("PT1H", calendar=calendar)
        self._create_sequence(task, task3, "FINISH_START")
        self._create_sequence(task2, task3, "FINISH_START")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task2.TaskTime.EarlyFinish == "2026-01-09T15:00:00"
        assert task2.TaskTime.LateFinish == "2026-01-12T11:00:00"
        assert task2.TaskTime.TotalFloat == "PT4H"  # Friday 15:00 to 17:00 and Monday 09:00 to 11:00
        assert task2.TaskTime.FreeFloat == "PT4H"
        assert task.TaskTime.TotalFloat == "P0D"

    def test_recalculating_for_a_single_task(self):
        self._add_work_schedule()
        task = self._create_task("P1D")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.cascade_schedule(self.file, task=task)
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
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

    def test_recalculating_finish_to_start_for_sub_day_durations(self):
        self._add_work_schedule()
        task = self._create_task("PT5H")
        task2 = self._create_task("PT5H")
        self._create_sequence(task, task2, "FINISH_START")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.EarlyStart == "2000-01-01T09:00:00"
        assert task.TaskTime.EarlyFinish == "2000-01-01T14:00:00"
        assert task.TaskTime.LateFinish == "2000-01-01T14:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-01T14:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-02T11:00:00"
        assert task2.TaskTime.LateStart == "2000-01-01T14:00:00"
        assert task2.TaskTime.LateFinish == "2000-01-02T11:00:00"

    def test_recalculating_finish_to_start_with_a_sub_day_lag(self):
        # Tasks of work hours: the lag gives an exact time. A task of work days would start at a day start.
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("PT8H")
        self._create_sequence(task, task2, "FINISH_START", lag="PT2H")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.LateFinish == "2000-01-01T17:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T11:00:00"
        assert task2.TaskTime.IsCritical is True

    def test_recalculating_finish_to_start_with_a_negative_sub_day_lag(self):
        # Tasks of work hours: the lag gives an exact time. A task of work days would start at a day start.
        self._add_work_schedule()
        task = self._create_task("P1D")
        task2 = self._create_task("PT8H")
        self._create_sequence(task, task2, "FINISH_START", lag="-PT2H")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task2.TaskTime.EarlyStart == "2000-01-01T15:00:00"
        assert task2.TaskTime.LateStart == "2000-01-01T15:00:00"
        assert task.TaskTime.IsCritical is True

    def test_recalculating_a_lag_as_a_ratio_of_the_predecessor_duration(self):
        # Tasks of work hours: the lag gives an exact time. A task of work days would start at a day start.
        self._add_work_schedule()
        task = self._create_task("PT8H")
        task2 = self._create_task("PT8H")
        self._create_sequence(task, task2, "FINISH_START", lag=0.5)
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task2.TaskTime.EarlyStart == "2000-01-02T13:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-03T13:00:00"

    def test_recalculating_with_the_work_day_duration_of_the_schedule(self):
        self._add_work_schedule()
        pset = ifcopenshell.api.pset.add_pset(self.file, product=self.work_schedule, name="Pset_WorkControlCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"WorkDayDuration": "PT10H"})
        task = self._create_task("P1D")
        task2 = self._create_task("P1D")
        self._create_sequence(task, task2, "FINISH_START")
        ifcopenshell.api.sequence.recalculate_schedule(self.file, work_schedule=self.work_schedule)
        assert task.TaskTime.EarlyFinish == "2000-01-01T19:00:00"
        assert task2.TaskTime.EarlyStart == "2000-01-02T09:00:00"
        assert task2.TaskTime.EarlyFinish == "2000-01-02T19:00:00"

    def _add_work_schedule(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        self.work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)

    def _create_task(self, duration, duration_type="WORKTIME", start=datetime.date(2000, 1, 1), calendar=None):
        task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=self.work_schedule)
        if duration == "P0D":
            task.IsMilestone = True
        if calendar:
            ifcopenshell.api.control.assign_control(self.file, relating_control=calendar, related_objects=[task])
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            self.file,
            task_time=task_time,
            attributes={"ScheduleStart": start, "ScheduleDuration": duration, "DurationType": duration_type},
        )
        return task

    def _create_sequence(self, predecessor, successor, relationship, lag=None, lag_type="WORKTIME"):
        rel = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )
        ifcopenshell.api.sequence.edit_sequence(self.file, rel_sequence=rel, attributes={"SequenceType": relationship})
        if isinstance(lag, float):  # An IfcRatioMeasure
            value = self.file.createIfcRatioMeasure(lag)
            rel.TimeLag = self.file.createIfcLagTime(DurationType=lag_type, LagValue=value)
        elif lag:
            ifcopenshell.api.sequence.assign_lag_time(
                self.file, rel_sequence=rel, lag_value=lag, duration_type=lag_type
            )
