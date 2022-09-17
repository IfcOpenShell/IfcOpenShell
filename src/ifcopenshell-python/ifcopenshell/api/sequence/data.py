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

import ifcopenshell.util.date


class Data:
    is_loaded = False
    work_schedules = {}
    work_calendars = {}
    work_times = {}
    recurrence_patterns = {}
    time_periods = {}
    tasks = {}
    task_times = {}
    lag_times = {}
    sequences = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.work_schedules = {}
        cls.work_calendars = {}
        cls.work_times = {}
        cls.recurrence_patterns = {}
        cls.time_periods = {}
        cls.tasks = {}
        cls.task_times = {}
        cls.lag_times = {}
        cls.sequences = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_work_schedules()
        cls.load_work_calendars()
        cls.load_work_times()
        cls.load_recurrence_patterns()
        cls.load_time_periods()
        cls.load_tasks()
        cls.load_task_times()
        cls.load_lag_times()
        cls.load_sequences()
        cls.is_loaded = True

    @classmethod
    def load_work_schedules(cls):
        cls.work_schedules = {}
        for work_schedule in cls._file.by_type("IfcWorkSchedule"):
            data = work_schedule.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(
                data["CreationDate"]
            )
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"])
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(
                    data["FinishTime"]
                )
            data["RelatedObjects"] = []
            for rel in work_schedule.Controls:
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcTask"):
                        data["RelatedObjects"].append(obj.id())
            cls.work_schedules[work_schedule.id()] = data

    @classmethod
    def load_work_calendars(cls):
        cls.work_calendars = {}
        for work_calendar in cls._file.by_type("IfcWorkCalendar"):
            data = work_calendar.get_info()
            del data["OwnerHistory"]
            data["WorkingTimes"] = [t.id() for t in work_calendar.WorkingTimes or []]
            data["ExceptionTimes"] = [
                t.id() for t in work_calendar.ExceptionTimes or []
            ]
            cls.work_calendars[work_calendar.id()] = data

    @classmethod
    def load_work_times(cls):
        cls.work_times = {}
        for work_time in cls._file.by_type("IfcWorkTime"):
            data = work_time.get_info()
            data["Start"] = (
                ifcopenshell.util.date.ifc2datetime(data["Start"])
                if data["Start"]
                else None
            )
            data["Finish"] = (
                ifcopenshell.util.date.ifc2datetime(data["Finish"])
                if data["Finish"]
                else None
            )
            data["RecurrencePattern"] = (
                work_time.RecurrencePattern.id()
                if work_time.RecurrencePattern
                else None
            )
            cls.work_times[work_time.id()] = data

    @classmethod
    def load_recurrence_patterns(cls):
        cls.recurrence_patterns = {}
        for recurrence_pattern in cls._file.by_type("IfcRecurrencePattern"):
            data = recurrence_pattern.get_info()
            data["TimePeriods"] = [t.id() for t in recurrence_pattern.TimePeriods or []]
            cls.recurrence_patterns[recurrence_pattern.id()] = data

    @classmethod
    def load_time_periods(cls):
        cls.time_periods = {}
        for time_period in cls._file.by_type("IfcTimePeriod"):
            cls.time_periods[time_period.id()] = {
                "StartTime": ifcopenshell.util.date.ifc2datetime(time_period.StartTime),
                "EndTime": ifcopenshell.util.date.ifc2datetime(time_period.EndTime),
            }

    @classmethod
    def load_tasks(cls):
        cls.tasks = {}
        for task in cls._file.by_type("IfcTask"):
            data = task.get_info()
            del data["OwnerHistory"]
            data["HasAssignmentsWorkCalendar"] = []
            data["RelatedObjects"] = []
            data["Inputs"] = []
            data["Controls"] = []
            data["Outputs"] = []
            data["Resources"] = []
            data["IsPredecessorTo"] = []
            data["IsSuccessorFrom"] = []
            if task.TaskTime:
                data["TaskTime"] = data["TaskTime"].id()
            for rel in task.IsNestedBy:
                [
                    data["RelatedObjects"].append(o.id())
                    for o in rel.RelatedObjects
                    if o.is_a("IfcTask")
                ]
            data["Nests"] = [r.RelatingObject.id() for r in task.Nests or []]
            [
                data["Outputs"].append(r.RelatingProduct.id())
                for r in task.HasAssignments
                if r.is_a("IfcRelAssignsToProduct")
            ]
            [
                data["Resources"].extend(
                    [o.id() for o in r.RelatedObjects if o.is_a("IfcResource")]
                )
                for r in task.OperatesOn
            ]
            [
                data["Controls"].extend(
                    [o.id() for o in r.RelatedObjects if o.is_a("IfcControl")]
                )
                for r in task.OperatesOn
            ]
            [
                data["Inputs"].extend(
                    [o.id() for o in r.RelatedObjects if o.is_a("IfcProduct")]
                )
                for r in task.OperatesOn
            ]
            [
                data["IsPredecessorTo"].append(rel.id())
                for rel in task.IsPredecessorTo or []
            ]
            [
                data["IsSuccessorFrom"].append(rel.id())
                for rel in task.IsSuccessorFrom or []
            ]
            [
                data["HasAssignmentsWorkCalendar"].append(rel.RelatingControl.id())
                for rel in task.HasAssignments or []
                if rel.is_a("IfcRelAssignsToControl")
                and rel.RelatingControl.is_a("IfcWorkCalendar")
            ]
            cls.tasks[task.id()] = data

    @classmethod
    def load_task_times(cls):
        cls.task_times = {}
        for task_time in cls._file.by_type("IfcTaskTime"):
            data = task_time.get_info()
            for key, value in data.items():
                if not value:
                    continue
                if "Start" in key or "Finish" in key or key == "StatusTime":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
                elif key == "ScheduleDuration":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
            cls.task_times[task_time.id()] = data

    @classmethod
    def load_lag_times(cls):
        cls.lag_times = {}
        for lag_time in cls._file.by_type("IfcLagTime"):
            data = lag_time.get_info()
            if data["LagValue"]:
                if data["LagValue"].is_a("IfcDuration"):
                    data["LagValue"] = ifcopenshell.util.date.ifc2datetime(
                        data["LagValue"].wrappedValue
                    )
                else:
                    data["LagValue"] = float(data["LagValue"].wrappedValue)
            cls.lag_times[lag_time.id()] = data

    @classmethod
    def load_sequences(cls):
        cls.sequences = {}
        for sequence in cls._file.by_type("IfcRelSequence"):
            data = sequence.get_info()
            data["RelatingProcess"] = sequence.RelatingProcess.id()
            data["RelatedProcess"] = sequence.RelatedProcess.id()
            data["TimeLag"] = sequence.TimeLag.id() if sequence.TimeLag else None
            cls.sequences[sequence.id()] = data
