# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2021-2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
import ifcopenshell


def refresh():
    SequenceData.is_loaded = False


class SequenceData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_work_plans": cls.has_work_plans(),
            "has_work_schedules": cls.has_work_schedules(),
            "has_work_calendars": cls.has_work_calendars(),
        }
        cls.load_work_plans()
        cls.load_work_schedules()
        cls.load_work_calendars()
        cls.load_work_times()
        cls.load_recurrence_patterns()
        cls.load_time_periods()
        cls.load_sequences()
        cls.load_lag_times()
        cls.load_task_times()
        cls.load_tasks()
        cls.is_loaded = True

    @classmethod
    def has_work_plans(cls):
        return bool(tool.Ifc.get().by_type("IfcWorkPlan"))

    @classmethod
    def has_work_calendars(cls):
        return bool(tool.Ifc.get().by_type("IfcWorkCalendar"))

    @classmethod
    def number_of_work_plans_loaded(cls):
        return len(tool.Ifc.get().by_type("IfcWorkPlan"))

    @classmethod
    def number_of_work_schedules_loaded(cls):
        return len(tool.Ifc.get().by_type("IfcWorkSchedule"))

    @classmethod
    def has_work_schedules(cls):
        return bool(tool.Ifc.get().by_type("IfcWorkSchedule"))

    @classmethod
    def load_work_plans(cls):
        cls.data["work_plans"] = {}
        for work_plan in tool.Ifc.get().by_type("IfcWorkPlan"):
            data = {"Name": work_plan.Name}
            data["IsDecomposedBy"] = []
            for rel in work_plan.IsDecomposedBy:
                data["IsDecomposedBy"].extend([o.id() for o in rel.RelatedObjects])
            cls.data["work_plans"][work_plan.id()] = data
        cls.data["number_of_work_plans_loaded"] = cls.number_of_work_plans_loaded()

    @classmethod
    def load_work_schedules(cls):
        cls.data["work_schedules"] = {}
        for work_schedule in tool.Ifc.get().by_type("IfcWorkSchedule"):
            data = work_schedule.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = (
                ifcopenshell.util.date.ifc2datetime(data["CreationDate"]) if data["CreationDate"] else ""
            )
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"]) if data["StartTime"] else ""
            data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"]) if data["FinishTime"] else ""
            data["RelatedObjects"] = []
            for rel in work_schedule.Controls:
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcTask"):
                        data["RelatedObjects"].append(obj.id())
            cls.data["work_schedules"][work_schedule.id()] = data

        cls.data["number_of_work_schedules_loaded"] = cls.number_of_work_schedules_loaded()

    @classmethod
    def load_work_calendars(cls):
        cls.data["work_calendars"] = {}
        for work_calendar in tool.Ifc.get().by_type("IfcWorkCalendar"):
            data = work_calendar.get_info()
            del data["OwnerHistory"]
            data["WorkingTimes"] = [t.id() for t in work_calendar.WorkingTimes or []]
            data["ExceptionTimes"] = [t.id() for t in work_calendar.ExceptionTimes or []]
            cls.data["work_calendars"][work_calendar.id()] = data

        cls.data["number_of_work_calendars_loaded"] = len(cls.data["work_calendars"].keys())

    @classmethod
    def load_work_times(cls):
        cls.data["work_times"] = {}
        for work_time in tool.Ifc.get().by_type("IfcWorkTime"):
            data = work_time.get_info()
            data["Start"] = ifcopenshell.util.date.ifc2datetime(data["Start"]) if data["Start"] else None
            data["Finish"] = ifcopenshell.util.date.ifc2datetime(data["Finish"]) if data["Finish"] else None
            data["RecurrencePattern"] = work_time.RecurrencePattern.id() if work_time.RecurrencePattern else None
            cls.data["work_times"][work_time.id()] = data

    @classmethod
    def load_recurrence_patterns(cls):
        cls.data["recurrence_patterns"] = {}
        for recurrence_pattern in tool.Ifc.get().by_type("IfcRecurrencePattern"):
            data = recurrence_pattern.get_info()
            data["TimePeriods"] = [t.id() for t in recurrence_pattern.TimePeriods or []]
            cls.data["recurrence_patterns"][recurrence_pattern.id()] = data

    @classmethod
    def load_sequences(cls):
        cls.data["sequences"] = {}
        for sequence in tool.Ifc.get().by_type("IfcRelSequence"):
            data = sequence.get_info()
            data["RelatingProcess"] = sequence.RelatingProcess.id()
            data["RelatedProcess"] = sequence.RelatedProcess.id()
            data["TimeLag"] = sequence.TimeLag.id() if sequence.TimeLag else None
            cls.data["sequences"][sequence.id()] = data

    @classmethod
    def load_time_periods(cls):
        cls.data["time_periods"] = {}
        for time_period in tool.Ifc.get().by_type("IfcTimePeriod"):
            cls.data["time_periods"][time_period.id()] = {
                "StartTime": ifcopenshell.util.date.ifc2datetime(time_period.StartTime),
                "EndTime": ifcopenshell.util.date.ifc2datetime(time_period.EndTime),
            }

    @classmethod
    def load_task_times(cls):
        cls.data["task_times"] = {}
        for task_time in tool.Ifc.get().by_type("IfcTaskTime"):
            data = task_time.get_info()
            for key, value in data.items():
                if not value:
                    continue
                if "Start" in key or "Finish" in key or key == "StatusTime":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
                elif key == "ScheduleDuration":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
            cls.data["task_times"][task_time.id()] = data

    @classmethod
    def load_lag_times(cls):
        cls.data["lag_times"] = {}
        for lag_time in tool.Ifc.get().by_type("IfcLagTime"):
            data = lag_time.get_info()
            if data["LagValue"]:
                if data["LagValue"].is_a("IfcDuration"):
                    data["LagValue"] = ifcopenshell.util.date.ifc2datetime(data["LagValue"].wrappedValue)
                else:
                    data["LagValue"] = float(data["LagValue"].wrappedValue)
            cls.data["lag_times"][lag_time.id()] = data

    @classmethod
    def load_tasks(cls):
        cls.data["tasks"] = {}
        for task in tool.Ifc.get().by_type("IfcTask"):
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
                [data["RelatedObjects"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcTask")]
            data["Nests"] = [r.RelatingObject.id() for r in task.Nests or []]
            [
                data["Outputs"].append(r.RelatingProduct.id())
                for r in task.HasAssignments
                if r.is_a("IfcRelAssignsToProduct")
            ]
            [
                data["Resources"].extend([o.id() for o in r.RelatedObjects if o.is_a("IfcResource")])
                for r in task.OperatesOn
            ]
            [
                data["Controls"].extend([o.id() for o in r.RelatedObjects if o.is_a("IfcControl")])
                for r in task.OperatesOn
            ]
            [data["Inputs"].extend([o.id() for o in r.RelatedObjects if o.is_a("IfcProduct")]) for r in task.OperatesOn]
            [data["IsPredecessorTo"].append(rel.id()) for rel in task.IsPredecessorTo or []]
            [data["IsSuccessorFrom"].append(rel.id()) for rel in task.IsSuccessorFrom or []]
            for rel in task.HasAssignments:
                if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl:
                    if rel.RelatingControl.is_a("IfcWorkCalendar"):
                        data["HasAssignmentsWorkCalendar"].append(rel.RelatingControl.id())
            cls.data["tasks"][task.id()] = data
