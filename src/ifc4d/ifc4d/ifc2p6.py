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
        self.starts = []
        self.finishes = []
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
        self.root.attrib["xsi:schemaLocation"] = (
            "http://xmlns.oracle.com/Primavera/P6Professional/V18.8/API/BusinessObjects http://xmlns.oracle.com/Primavera/P6Professional/V18.8/API/p6apibo.xsd"
        )

        self.schedule = self.file.by_type("IfcWorkSchedule")[0]

        # It seems as though OBSes aren't necessary and cause permission issues on P6 enterprise setups
        # self.create_obs()
        self.create_projects()

        tree = ET.ElementTree(self.root)
        tree.write(self.xml, encoding="utf-8", xml_declaration=True)

    def create_obs(self):
        element = self.file.by_type("IfcProject")[0]
        obs = ET.SubElement(self.root, "OBS")
        self.link_element(element, obs)
        ET.SubElement(obs, "Id").text = element.Name or "X"
        ET.SubElement(obs, "Name").text = element.LongName or "Unnamed"

    def create_calendars(self, work_schedule):
        for calendar in self.file.by_type("IfcWorkCalendar"):
            self.create_calendar(calendar, work_schedule)

    def create_calendar(self, calendar, work_schedule):
        el = ET.SubElement(self.element_map[work_schedule], "Calendar")
        ET.SubElement(el, "Name").text = calendar.Name or "Unnamed"
        self.link_element(calendar, el)
        ET.SubElement(el, "BaseCalendarObjectId")
        ET.SubElement(el, "HoursPerDay").text = "8"
        ET.SubElement(el, "HoursPerMonth").text = "172"
        ET.SubElement(el, "HoursPerWeek").text = "40"
        ET.SubElement(el, "HoursPerYear").text = "2000"
        ET.SubElement(el, "IsDefault").text = "0"
        ET.SubElement(el, "IsPersonal").text = "0"
        ET.SubElement(el, "ProjectObjectId").text = self.id_map[work_schedule]
        ET.SubElement(el, "Type").text = "Project"

        working_week = self.auto_detect_working_week(calendar)

        if not working_week:
            working_week = self.get_default_working_week()

        work_week = ET.SubElement(el, "StandardWorkWeek")

        for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
            work_hours = ET.SubElement(work_week, "StandardWorkHours")
            ET.SubElement(work_hours, "DayOfWeek").text = day
            if day in working_week:
                print(working_week)
                for time_period in working_week[day]:
                    work_time = ET.SubElement(work_hours, "WorkTime")
                    ET.SubElement(work_time, "Start").text = time_period["Start"]
                    ET.SubElement(work_time, "Finish").text = time_period["Finish"]
            else:
                ET.SubElement(work_hours, "WorkTime")

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
        for working_time in calendar.WorkingTimes or []:
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
        if finish < start:
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
        activity_calendar = ET.SubElement(project, "ActivityDefaultCalendarObjectId")
        ET.SubElement(project, "Name").text = work_schedule.Name or "Unnamed"
        ET.SubElement(project, "Id").text = work_schedule.Identification or "X"
        data_date = ET.SubElement(project, "DataDate")
        planned_start_date = ET.SubElement(project, "PlannedStartDate")
        # ET.SubElement(project, "OBSObjectId").text = self.id_map[self.file.by_type("IfcProject")[0]]

        # Note: order matters for P6 enterprise imports.
        # Root elements like Name must come first. Then calendar, WBS, activities, and relationships.
        # Changing the order will result in import failures (but not for all P6 versions, it seems?)
        self.create_calendars(work_schedule)
        self.project_tasks = []
        self.activities = []
        self.create_wbs(self.get_subtasks(work_schedule), work_schedule)
        self.create_activities()
        self.create_relationships(self.project_tasks, work_schedule)

        activity_calendar.text = self.id_map[self.file.by_type("IfcWorkCalendar")[0]]
        start_date = sorted(self.starts)[0]
        data_date.text = start_date
        planned_start_date.text = start_date

    def create_wbs(self, tasks, work_schedule, parent=None):
        self.project_tasks.extend(tasks)
        for task in tasks:
            subtasks = self.get_subtasks(task)
            if not subtasks and task.TaskTime:
                self.activities.append({"task": task, "work_schedule": work_schedule, "parent": parent})
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

    def create_activities(self):
        for activity in self.activities:
            self.create_activity(activity["task"], activity["work_schedule"], parent=activity["parent"])

    def create_activity(self, task, work_schedule, parent=None):
        activity = ET.SubElement(self.element_map[work_schedule], "Activity")
        self.link_element(task, activity)
        ET.SubElement(activity, "Id").text = task.Identification or "X"
        ET.SubElement(activity, "Name").text = task.Name or "Unnamed"
        if parent:
            ET.SubElement(activity, "WBSObjectId").text = self.id_map[parent]
        if task.TaskTime.ScheduleDuration:
            duration = ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration)
            ET.SubElement(activity, "PlannedDuration").text = str(duration.days * self.hours_per_day)
            ET.SubElement(activity, "RemainingDuration").text = str(duration.days * self.hours_per_day)
        if task.TaskTime.ScheduleStart:
            ET.SubElement(activity, "PlannedStartDate").text = task.TaskTime.ScheduleStart
            ET.SubElement(activity, "StartDate").text = task.TaskTime.ScheduleStart
            self.starts.append(task.TaskTime.ScheduleStart)
        if task.TaskTime.ScheduleFinish:
            ET.SubElement(activity, "PlannedFinishDate").text = task.TaskTime.ScheduleFinish
            ET.SubElement(activity, "FinishDate").text = task.TaskTime.ScheduleFinish
            self.finishes.append(task.TaskTime.ScheduleFinish)
        data_map = {
            "RemainingEarlyStartDate": task.TaskTime.EarlyStart,
            "RemainingEarlyFinishDate": task.TaskTime.EarlyFinish,
            "RemainingLateStartDate": task.TaskTime.LateStart,
            "RemainingLateFinishDate": task.TaskTime.LateFinish,
        }
        for key, value in data_map.items():
            el = ET.SubElement(activity, key)
            if value:
                el.text = value
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
                ET.SubElement(relationship, "PredecessorProjectObjectId").text = self.id_map[work_schedule]
                ET.SubElement(relationship, "SuccessorProjectObjectId").text = self.id_map[work_schedule]
                ET.SubElement(relationship, "PredecessorActivityObjectId").text = self.id_map[predecessor]
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
        guid = str(uuid.UUID(ifcopenshell.guid.expand(element.GlobalId))).upper()
        ET.SubElement(el, "GUID").text = "{" + guid + "}"
        self.id_map[element] = str(self.id)
        self.element_map[element] = el
        return self.id
