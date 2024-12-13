# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2021-2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.date
from ifcopenshell.util.doc import get_predefined_type_doc
import json
from typing import Any


def refresh():
    SequenceData.is_loaded = False
    WorkPlansData.is_loaded = False
    TaskICOMData.is_loaded = False
    WorkScheduleData.is_loaded = False
    AnimationColorSchemeData.is_loaded = False


class SequenceData:
    data: dict[str, Any] = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_work_plans": cls.has_work_plans(),
            "has_work_schedules": cls.has_work_schedules(),
            "has_work_calendars": cls.has_work_calendars(),
            "schedule_predefined_types_enum": cls.schedule_predefined_types_enum(),
            "task_columns_enum": cls.task_columns_enum(),
            "tasktimecolumns_enum": cls.tasktimecolumns_enum(),
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
            data = {"Name": work_plan.Name or "Unnamed"}
            data["IsDecomposedBy"] = []
            for rel in work_plan.IsDecomposedBy:
                data["IsDecomposedBy"].extend([o.id() for o in rel.RelatedObjects])
            cls.data["work_plans"][work_plan.id()] = data
        cls.data["number_of_work_plans_loaded"] = cls.number_of_work_plans_loaded()

    @classmethod
    def load_work_schedules(cls):
        cls.data["work_schedules"] = {}
        cls.data["work_schedules_enum"] = []
        for work_schedule in tool.Ifc.get().by_type("IfcWorkSchedule"):
            data = work_schedule.get_info()
            if not data["Name"]:
                data["Name"] = "Unnamed"
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
            cls.data["work_schedules_enum"].append((str(work_schedule.id()), data["Name"], ""))

        cls.data["number_of_work_schedules_loaded"] = cls.number_of_work_schedules_loaded()

    @classmethod
    def load_work_calendars(cls):
        cls.data["work_calendars"] = {}
        cls.data["work_calendars_enum"] = []
        for work_calendar in tool.Ifc.get().by_type("IfcWorkCalendar"):
            data = work_calendar.get_info()
            del data["OwnerHistory"]
            if not data["Name"]:
                data["Name"] = "Unnamed"
            data["WorkingTimes"] = [t.id() for t in work_calendar.WorkingTimes or []]
            data["ExceptionTimes"] = [t.id() for t in work_calendar.ExceptionTimes or []]
            cls.data["work_calendars"][work_calendar.id()] = data
            cls.data["work_calendars_enum"].append((str(work_calendar.id()), data["Name"], ""))

        cls.data["number_of_work_calendars_loaded"] = len(cls.data["work_calendars"].keys())

    @classmethod
    def load_work_times(cls):
        cls.data["work_times"] = {}
        for work_time in tool.Ifc.get().by_type("IfcWorkTime"):
            data = work_time.get_info()
            if tool.Ifc.get_schema() == "IFC4X3":
                start_date, finish_date = data["StartDate"], data["FinishDate"]
            else:
                start_date, finish_date = data["Start"], data["Finish"]
            data["Start"] = ifcopenshell.util.date.ifc2datetime(start_date) if start_date else None
            data["Finish"] = ifcopenshell.util.date.ifc2datetime(finish_date) if finish_date else None
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
            data["NestingIndex"] = None
            for rel in task.Nests or []:
                data["NestingIndex"] = rel.RelatedObjects.index(task)
            cls.data["tasks"][task.id()] = data

    @classmethod
    def schedule_predefined_types_enum(cls) -> list[tuple[str, str, str]]:
        results: list[tuple[str, str, str]] = []
        declaration = tool.Ifc().schema().declaration_by_name("IfcWorkSchedule")
        version = tool.Ifc.get_schema()
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                results.extend(
                    [
                        (e, e, get_predefined_type_doc(version, "IfcWorkSchedule", e))
                        for e in ifcopenshell.util.attribute.get_enum_items(attribute)
                        if e != "BASELINE"
                    ]
                )
                break
        return results

    @classmethod
    def task_columns_enum(cls) -> list[tuple[str, str, str]]:
        schema = tool.Ifc.schema()
        taskcolumns_enum = []
        for a in schema.declaration_by_name("IfcTask").all_attributes():
            if (primitive_type := ifcopenshell.util.attribute.get_primitive_type(a)) not in (
                "string",
                "float",
                "integer",
                "boolean",
                "enum",
            ):
                continue
            taskcolumns_enum.append((f"{a.name()}/{primitive_type}", a.name(), ""))
        return taskcolumns_enum

    @classmethod
    def tasktimecolumns_enum(cls) -> list[tuple[str, str, str]]:
        schema = tool.Ifc.schema()
        tasktimecolumns_enum = []
        for a in schema.declaration_by_name("IfcTaskTime").all_attributes():
            if (primitive_type := ifcopenshell.util.attribute.get_primitive_type(a)) not in (
                "string",
                "float",
                "integer",
                "boolean",
                "enum",
            ):
                continue
            tasktimecolumns_enum.append((f"{a.name()}/{primitive_type}", a.name(), ""))
        return tasktimecolumns_enum


class WorkScheduleData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "can_have_baselines": cls.can_have_baselines(),
            "active_work_schedule_baselines": cls.active_work_schedule_baselines(),
        }
        cls.is_loaded = True

    @classmethod
    def can_have_baselines(cls):
        if not bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
            return False
        return (
            tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id).PredefinedType
            == "PLANNED"
        )

    @classmethod
    def active_work_schedule_baselines(cls):
        results = []
        if not bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
            return []
        for rel in tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id).Declares:
            for work_schedule in rel.RelatedObjects:
                if work_schedule.PredefinedType == "BASELINE":
                    results.append(
                        {
                            "id": work_schedule.id(),
                            "name": work_schedule.Name or "Unnamed",
                            "date": str(ifcopenshell.util.date.ifc2datetime(work_schedule.CreationDate)),
                        }
                    )
        return results


class WorkPlansData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_work_plans": cls.total_work_plans(),
            "work_plans": cls.work_plans(),
            "has_work_schedules": cls.has_work_schedules(),
            "active_work_plan_schedules": cls.active_work_plan_schedules(),
        }
        cls.is_loaded = True

    @classmethod
    def total_work_plans(cls):
        return len(tool.Ifc.get().by_type("IfcWorkPlan"))

    @classmethod
    def work_plans(cls):
        results = []
        for work_plan in tool.Ifc.get().by_type("IfcWorkPlan"):
            results.append({"id": work_plan.id(), "name": work_plan.Name or "Unnamed"})
        return results

    @classmethod
    def has_work_schedules(cls):
        return len(tool.Ifc.get().by_type("IfcWorkSchedule"))

    @classmethod
    def active_work_plan_schedules(cls):
        results = []
        if not bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id:
            return []
        for rel in tool.Ifc.get().by_id(bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id).IsDecomposedBy:
            for work_schedule in rel.RelatedObjects:
                results.append({"id": work_schedule.id(), "name": work_schedule.Name or "Unnamed"})
        return results


class TaskICOMData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"can_active_resource_be_assigned": cls.can_active_resource_be_assigned()}
        cls.is_loaded = True

    @classmethod
    def can_active_resource_be_assigned(cls):
        resource_props = bpy.context.scene.BIMResourceProperties
        resource_tprops = bpy.context.scene.BIMResourceTreeProperties
        total_resources = len(resource_tprops.resources)
        if total_resources and resource_props.active_resource_index < total_resources:
            resource_id = resource_tprops.resources[resource_props.active_resource_index].ifc_definition_id
            return not tool.Ifc.get().by_id(resource_id).is_a("IfcCrewResource")
        return False


class AnimationColorSchemeData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["saved_color_schemes"] = cls.saved_color_schemes()

    @classmethod
    def saved_color_schemes(cls):
        groups = tool.Ifc.get().by_type("IfcGroup")
        results = []
        for group in groups:
            try:
                data = json.loads(group.Description)
                if (
                    isinstance(data, dict)
                    and data.get("type", None) == "BBIM_AnimationColorScheme"
                    and data.get("colourscheme", None)
                ):
                    results.append(group)
            except:
                pass
        return [(str(g.id()), g.Name or "Unnamed", "") for g in sorted(results, key=lambda x: x.Name or "Unnamed")]
