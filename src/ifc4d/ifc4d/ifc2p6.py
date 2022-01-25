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
import datetime
import ifcopenshell
import ifcopenshell.util.date
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

    def execute(self):
        self.root = ET.Element("APIBusinessObjects")
        self.schedule = self.file.by_type("IfcWorkSchedule")[0]

        self.create_obs()
        self.create_calendars()
        self.create_projects()

        tree = ET.ElementTree(self.root)
        tree.write(self.xml)

    def create_obs(self):
        element = self.file.by_type("IfcProject")[0]
        obs = ET.SubElement(self.root, "OBS")
        self.link_element(element, obs)
        ET.SubElement(obs, "Name").text = element.Name or "Unnamed"

    def create_calendars(self):
        for calendar in self.file.by_type("IfcWorkCalendar"):
            self.create_calendar(calendar)

    def create_calendar(self, calendar):
        el = ET.SubElement(self.root, "Calendar")
        ET.SubElement(el, "Name").text = calendar.Name or "Unnamed"
        self.link_element(calendar, el)

        # Hardcode for now
        work_week = ET.SubElement(el, "StandardWorkWeek")

        work_hours = ET.SubElement(work_week, "StandardWorkHours")
        day = ET.SubElement(work_hours, "DayOfWeek").text = "Sunday"

        for name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
            work_hours = ET.SubElement(work_week, "StandardWorkHours")
            day = ET.SubElement(work_hours, "DayOfWeek").text = name
            work_time = ET.SubElement(work_hours, "WorkTime")
            ET.SubElement(work_time, "Start").text = "08:00:00"
            ET.SubElement(work_time, "Finish").text = "17:00:00"

        holidays = ET.SubElement(el, "HolidayOrExceptions")

        holiday = ET.SubElement(holidays, "HolidayOrException")
        date = ET.SubElement(holidays, "Date").text = "2022-01-01T00:00:00"

        holiday = ET.SubElement(holidays, "HolidayOrException")
        date = ET.SubElement(holidays, "Date").text = "2022-01-02T00:00:00"

        holiday = ET.SubElement(holidays, "HolidayOrException")
        date = ET.SubElement(holidays, "Date").text = "2022-01-03T00:00:00"

    def create_projects(self):
        for work_schedule in self.file.by_type("IfcWorkSchedule"):
            self.create_project(work_schedule)

    def create_project(self, work_schedule):
        project = ET.SubElement(self.root, "Project")
        self.link_element(work_schedule, project)

        ET.SubElement(project, "ActivityDefaultCalendarObjectId").text = self.id_map[self.file.by_type("IfcWorkCalendar")[0]]
        ET.SubElement(project, "Name").text = work_schedule.Name or "Unnamed"
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
            if parent:
                ET.SubElement(wbs, "ParentObjectId").text = self.id_map[parent]
            ET.SubElement(wbs, "ProjectObjectId").text = self.id_map[work_schedule]
            self.create_wbs(subtasks, work_schedule, parent=task)

    def create_activity(self, task, work_schedule, parent=None):
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
            if task.TaskTime.ScheduleStart:
                ET.SubElement(activity, "PlannedStartDate").text = task.TaskTime.ScheduleStart
                ET.SubElement(activity, "StartDate").text = task.TaskTime.ScheduleStart
            if task.TaskTime.ScheduleFinish:
                ET.SubElement(activity, "PlannedFinishDate").text = task.TaskTime.ScheduleFinish
                ET.SubElement(activity, "FinishDate").text = task.TaskTime.ScheduleFinish
        ET.SubElement(activity, "ProjectObjectId").text = self.id_map[work_schedule]

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
        self.id_map[element] = str(self.id)
        self.element_map[element] = el
        return self.id
