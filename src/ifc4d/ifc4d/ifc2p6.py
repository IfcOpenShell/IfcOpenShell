# Ifc4D - IFC scheduling utility
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc4D.
#
# Ifc4D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc4D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc4D.  If not, see <http://www.gnu.org/licenses/>.

import math
import uuid
import datetime
import ifcopenshell
import ifcopenshell.util.date
import ifcopenshell.util.sequence
import xml.etree.ElementTree as ET
from .common import ScheduleIfcGenerator


class Ifc2P6:
    def __init__(self):
        self.xml = None
        self.file = None
        self.id = 0
        self.id_map = {}
        self.element_map = {}
        self.hours_per_day = 8
        self.project_tasks = []
        # P6XML does not understand patterns in holiday dates. Instead, it
        # expects a list of every day that is a holiday between a date range.
        # This allows you to specify the date range where the export should
        # calculate holidays for.
        self.holiday_start_date = None
        self.holiday_finish_date = None

    def execute(self):
        self.root = ET.Element("APIBusinessObjects")
        self.root.attrib["xmlns"] = "http://xmlns.oracle.com/Primavera/P6Professional/V18.8/API/BusinessObjects"
        self.root.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        self.root.attrib[
            "xsi:schemaLocation"
        ] = "http://xmlns.oracle.com/Primavera/P6Professional/V18.8/API/BusinessObjects http://xmlns.oracle.com/Primavera/P6Professional/V18.8/API/p6apibo.xsd"

        self.schedule = self.file.by_type("IfcWorkSchedule")[0]

        self.create_obs()
        self.create_calendars()
        self.create_projects()

        tree = ET.ElementTree(self.root)
        tree.write(self.xml, encoding="utf-8", xml_declaration=True)

    def create_obs(self):
        element = self.file.by_type("IfcProject")[0]
        obs = ET.SubElement(self.root, "OBS")
        self.link_element(element, obs)
        ET.SubElement(obs, "Id").text = element.Name or "X"
        ET.SubElement(obs, "Name").text = element.LongName or "Unnamed"

    def create_calendars(self):
        for calendar in self.file.by_type("IfcWorkCalendar"):
            self.create_calendar(calendar)

    def create_calendar(self, calendar):
        el = ET.SubElement(self.root, "Calendar")
        ET.SubElement(el, "Name").text = calendar.Name or "Unnamed"
        self.link_element(calendar, el)

        working_week = self.auto_detect_working_week(calendar)

        if not working_week:
            working_week = self.get_default_working_week()

        work_week = ET.SubElement(el, "StandardWorkWeek")

        for day, time_periods in working_week.items():
            work_hours = ET.SubElement(work_week, "StandardWorkHours")
            day = ET.SubElement(work_hours, "DayOfWeek").text = day
            for time_period in time_periods:
                work_time = ET.SubElement(work_hours, "WorkTime")
                ET.SubElement(work_time, "Start").text = time_period["Start"]
                ET.SubElement(work_time, "Finish").text = time_period["Finish"]

        holidays = ET.SubElement(el, "HolidayOrExceptions")
        for holiday in self.auto_detect_holidays(calendar):
            el = ET.SubElement(holidays, "HolidayOrException")
            ET.SubElement(el, "Date").text = ifcopenshell.util.date.datetime2ifc(holiday, "IfcDateTime")
            ET.SubElement(el, "WorkTime")

    def auto_detect_working_week(self, calendar):
        # P6 XML only understands a working week. In other words, it understands
        # the equivalent of an IFC weekly recurring time period. If you do not
        # have a weekly recurring time period, we just give a default working
        # week.
        results = {}
        weekday_component_map = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday",
        }

        if not calendar.WorkingTimes:
            return None

        for working_time in calendar.WorkingTimes:
            if not working_time.RecurrencePattern or working_time.RecurrencePattern.RecurrenceType != "WEEKLY":
                continue

            if not working_time.RecurrencePattern.TimePeriods:
                time_periods = [{"Start": "09:00:00", "Finish": "17:00:00"}]
            else:
                time_periods = [
                    {"Start": p.StartTime, "Finish": p.EndTime} for p in working_time.RecurrencePattern.TimePeriods
                ]

            for component in working_time.RecurrencePattern.WeekdayComponent:
                results.setdefault(weekday_component_map[component], []).extend(time_periods)

        return results

    def get_default_working_week(self):
        results = {}
        # As a fallback, we work 5 days a week, 8 hours per day.
        for name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            results[name] = [{"Start": "09:00:00", "Finish": "17:00:00"}]
        return results

    def auto_detect_holidays(self, calendar):
        results = []
        start = self.holiday_start_date
        finish = self.holiday_finish_date
        if not finish or not start or finish < start:
            return results
        while start < finish:
            start += datetime.timedelta(days=1)
            if not ifcopenshell.util.sequence.is_working_day(start, calendar):
                results.append(start)
        return results

    def create_projects(self):
        for work_schedule in self.file.by_type("IfcWorkSchedule"):
            self.create_project(work_schedule)

    def create_project(self, work_schedule):
        project = ET.SubElement(self.root, "Project")
        self.link_element(work_schedule, project)

        ET.SubElement(project, "ActivityDefaultCalendarObjectId").text = self.id_map[
            self.file.by_type("IfcWorkCalendar")[0]
        ]
        ET.SubElement(project, "Name").text = work_schedule.Name or "Unnamed"
        ET.SubElement(project, "Id").text = work_schedule.Identification or "X"
        ET.SubElement(project, "OBSObjectId").text = self.id_map[self.file.by_type("IfcProject")[0]]

        self.project_tasks = []
        self.create_wbs(self.get_subtasks(work_schedule), work_schedule)
        self.create_relationships(self.project_tasks, work_schedule)

    def create_wbs(self, tasks, work_schedule, parent=None):
        self.project_tasks.extend(tasks)
        for task in tasks:
            subtasks = self.get_subtasks(task)
            if not subtasks:
                self.create_activity(task, work_schedule, parent=parent)
                continue
            wbs = ET.SubElement(self.element_map[work_schedule], "WBS")
            self.link_element(task, wbs)
            ET.SubElement(wbs, "Code").text = task.Identification or "X"
            ET.SubElement(wbs, "Name").text = task.Name or "Unnamed"
            parent_object_id = ET.SubElement(wbs, "ParentObjectId")
            if parent:
                parent_object_id.text = self.id_map[parent]
            ET.SubElement(wbs, "ProjectObjectId").text = self.id_map[work_schedule]
            self.create_wbs(subtasks, work_schedule, parent=task)

    def create_activity(self, task, work_schedule, parent=None):
        if not parent:
            return
        activity = ET.SubElement(self.element_map[work_schedule], "Activity")
        self.link_element(task, activity)
        ET.SubElement(activity, "Id").text = task.Identification or "X"
        ET.SubElement(activity, "Name").text = task.Name or "Unnamed"
        if parent:
            ET.SubElement(activity, "WBSObjectId").text = self.id_map[parent]
        if task.TaskTime:
            if task.TaskTime.ScheduleDuration:
                duration = ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration)
                ET.SubElement(activity, "PlannedDuration").text = str(duration.days * self.hours_per_day)
                ET.SubElement(activity, "RemainingDuration").text = str(duration.days * self.hours_per_day)
            if task.TaskTime.ScheduleStart:
                ET.SubElement(activity, "PlannedStartDate").text = task.TaskTime.ScheduleStart
                ET.SubElement(activity, "StartDate").text = task.TaskTime.ScheduleStart
            if task.TaskTime.ScheduleFinish:
                ET.SubElement(activity, "PlannedFinishDate").text = task.TaskTime.ScheduleFinish
                ET.SubElement(activity, "FinishDate").text = task.TaskTime.ScheduleFinish
        ET.SubElement(activity, "ProjectObjectId").text = self.id_map[work_schedule]
        ET.SubElement(activity, "ActualDuration").text = "0"
        ET.SubElement(activity, "ActualFinishDate")
        ET.SubElement(activity, "ActualStartDate")
        calendar = ifcopenshell.util.sequence.derive_calendar(task)
        if calendar:
            ET.SubElement(activity, "CalendarObjectId").text = self.id_map[calendar]
        ET.SubElement(activity, "DurationPercentComplete").text = "0"
        ET.SubElement(activity, "Type").text = "Task Dependent"
        ET.SubElement(activity, "Status").text = "Not Started"

        data_map = {}
        if task.TaskTime:
            data_map = {
                "RemainingEarlyStartDate": task.TaskTime.EarlyStart,
                "RemainingEarlyFinishDate": task.TaskTime.EarlyFinish,
                "RemainingLateStartDate": task.TaskTime.LateStart,
                "RemainingLateFinishDate": task.TaskTime.LateFinish,
            }

        for key, value in data_map.items():
            el = ET.SubElement(activity, "RemainingEarlyStartDate")
            if value:
                el.text = value

        if task.OperatesOn:
            assignsToProcess = ET.SubElement(activity, "AssignsToProcess")
            for proc in task.OperatesOn:
                process = ET.SubElement(assignsToProcess, "Process")
                ET.SubElement(process, "GlobalId").text = proc.GlobalId
                for obj in proc.RelatedObjects:
                    relObj = ET.SubElement(process, "RelatedObject")
                    ET.SubElement(relObj, "GlobalId").text = obj.GlobalId

    def create_relationships(self, tasks, work_schedule):
        for task in tasks:
            for rel in task.IsSuccessorFrom or []:
                predecessor = rel.RelatingProcess
                relationship = ET.SubElement(self.element_map[work_schedule], "Relationship")
                self.link_element(rel, relationship)
                if rel.TimeLag and rel.TimeLag.LagValue:
                    duration = ifcopenshell.util.date.ifc2datetime(rel.TimeLag.LagValue.wrappedValue)
                    ET.SubElement(relationship, "Lag").text = str(duration.days * self.hours_per_day)
                else:
                    ET.SubElement(relationship, "Lag").text = "0"
                if work_schedule in self.id_map:
                    ET.SubElement(relationship, "PredecessorProjectObjectId").text = self.id_map[work_schedule]
                    ET.SubElement(relationship, "SuccessorProjectObjectId").text = self.id_map[work_schedule]
                if predecessor in self.id_map:
                    ET.SubElement(relationship, "PredecessorActivityObjectId").text = self.id_map[predecessor]
                if task in self.id_map:
                    ET.SubElement(relationship, "SuccessorActivityObjectId").text = self.id_map[task]
                ET.SubElement(relationship, "Type").text = {
                    "START_START": "Start to Start",
                    "START_FINISH": "Start to Finish",
                    "FINISH_START": "Finish to Start",
                    "FINISH_FINISH": "Finish to Finish",
                    None: "Finish to Start",
                }[rel.SequenceType]

    def get_subtasks(self, element):
        tasks = []
        if element.is_a("IfcWorkSchedule"):
            for rel in element.Controls or []:
                tasks.extend([e for e in rel.RelatedObjects if e.is_a("IfcTask")])
        elif element.is_a("IfcTask"):
            for rel in element.IsNestedBy or []:
                tasks.extend([e for e in rel.RelatedObjects if e.is_a("IfcTask")])
        return tasks

    def link_element(self, element, el):
        self.id += 1
        ET.SubElement(el, "ObjectId").text = str(self.id)
        try:
            guid = str(uuid.UUID(ifcopenshell.guid.expand(element.GlobalId))).upper()
        except:
            guid = str(element.GlobalId)
        ET.SubElement(el, "GUID").text = "{" + guid + "}"
        self.id_map[element] = str(self.id)
        self.element_map[element] = el
        return self.id
