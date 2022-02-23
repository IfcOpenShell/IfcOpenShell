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
import test.bootstrap
import ifcopenshell.api


class TestEditTaskTime(test.bootstrap.IFC4):
    def test_editing_all_attributes(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "Name": "Name",
                "DataOrigin": "NOTDEFINED",
                "UserDefinedDataOrigin": "UserDefinedDataOrigin",
                "DurationType": "ELAPSEDTIME",
                "ScheduleDuration": "P1D",
                "ScheduleStart": "2000-01-01T00:00:00",
                "ScheduleFinish": "2000-01-02T00:00:00",
                "EarlyStart": "2000-01-01T00:00:00",
                "EarlyFinish": "2000-01-02T00:00:00",
                "LateStart": "2000-01-01T00:00:00",
                "LateFinish": "2000-01-02T00:00:00",
                "FreeFloat": "P0D",
                "TotalFloat": "P0D",
                "IsCritical": True,
                "StatusTime": "2000-01-01T00:00:00",
                "ActualDuration": "P1D",
                "ActualStart": "2000-01-01T00:00:00",
                "ActualFinish": "2000-01-02T00:00:00",
                "RemainingTime": "P1D",
                "Completion": 0.5,
            },
        )
        assert task_time.Name == "Name"
        assert task_time.DataOrigin == "NOTDEFINED"
        assert task_time.UserDefinedDataOrigin == "UserDefinedDataOrigin"
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P1D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-02T00:00:00"
        assert task_time.EarlyStart == "2000-01-01T00:00:00"
        assert task_time.EarlyFinish == "2000-01-02T00:00:00"
        assert task_time.LateStart == "2000-01-01T00:00:00"
        assert task_time.LateFinish == "2000-01-02T00:00:00"
        assert task_time.FreeFloat == "P0D"
        assert task_time.TotalFloat == "P0D"
        assert task_time.IsCritical == True
        assert task_time.StatusTime == "2000-01-01T00:00:00"
        assert task_time.ActualDuration == "P1D"
        assert task_time.ActualStart == "2000-01-01T00:00:00"
        assert task_time.ActualFinish == "2000-01-02T00:00:00"
        assert task_time.RemainingTime == "P1D"
        assert task_time.Completion == 0.5

    def test_editing_just_a_start_date_with_no_duration_or_finish(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleDuration": None,
                "ScheduleStart": "2000-01-01T00:00:00",
                "ScheduleFinish": None,
            },
        )
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish is None
        assert task_time.ScheduleDuration is None

    def test_editing_just_a_start_date_with_no_duration_or_finish_but_with_a_calendar(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        calendar = ifcopenshell.api.run("sequence.add_work_calendar", self.file)
        task = self.file.createIfcTask()
        ifcopenshell.api.run("control.assign_control", self.file, relating_control=calendar, related_object=task)
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task)
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleDuration": None,
                "ScheduleStart": datetime.datetime(2000, 1, 1),
                "ScheduleFinish": None,
            },
        )
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish is None
        assert task_time.ScheduleDuration is None

    def test_schedule_finish_dates_are_auto_calculated_if_possible(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "DurationType": "ELAPSEDTIME",
                "ScheduleDuration": "P1D",
                "ScheduleStart": "2000-01-01T00:00:00",
            },
        )
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P1D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-02T00:00:00"

    def test_schedule_durations_are_auto_calculated_if_possible(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "DurationType": "ELAPSEDTIME",
                "ScheduleStart": "2000-01-01T00:00:00",
                "ScheduleFinish": "2000-01-02T00:00:00",
            },
        )
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P1D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-02T00:00:00"

    def test_a_duration_takes_priority_over_start_and_finish_dates(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "DurationType": "ELAPSEDTIME",
                "ScheduleDuration": "P1D",
                "ScheduleStart": "2000-01-01T00:00:00",
                "ScheduleFinish": "2000-01-03T00:00:00",
            },
        )
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P1D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-02T00:00:00"

    def test_durations_can_be_specified_in_datetime_objects(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "DurationType": "ELAPSEDTIME",
                "ScheduleDuration": datetime.timedelta(days=1),
                "ScheduleStart": "2000-01-01T00:00:00",
            },
        )
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P1D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-02T00:00:00"

    def test_zero_durations_are_allowed(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.createIfcTask())
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "DurationType": "ELAPSEDTIME",
                "ScheduleDuration": datetime.timedelta(),
                "ScheduleStart": "2000-01-01T00:00:00",
            },
        )
        assert task_time.DurationType == "ELAPSEDTIME"
        assert task_time.ScheduleDuration == "P0D"
        assert task_time.ScheduleStart == "2000-01-01T00:00:00"
        assert task_time.ScheduleFinish == "2000-01-01T00:00:00"
