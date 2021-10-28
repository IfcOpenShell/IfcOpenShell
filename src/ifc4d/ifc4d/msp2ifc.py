
# Ifc4D - IFC scheduling utility
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import datetime
from datetime import timedelta
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import xml.etree.ElementTree as ET
from common import ScheduleIfcGenerator


class MSP2Ifc:
    def __init__(self):
        self.xml = None
        self.file = None
        self.ns = None
        self.work_plan = None
        self.project = {}
        self.calendars = {}
        self.wbs = {}
        self.root_activites = []
        self.tasks = {}
        self.relationships = {}

    def execute(self):
        self.parse_xml()
        ifcCreator = ScheduleIfcGenerator(self.file, self.work_plan, self.project, self.calendars,
                           self.wbs, self.root_activites, self.activities, self.relationships)
        ifcCreator.create_ifc()
        #self.create_ifc()

    def parse_xml(self):
        tree = ET.parse(self.xml)
        project = tree.getroot()
        self.ns = {"pr": project.tag[1:].partition("}")[0]}
        self.project["Name"] = project.find("pr:Name", self.ns).text
        self.outline_level = 0
        self.outline_parents = {}
        self.parse_task_xml(project)
        self.parse_calendar_xml(project)

    def parse_relationship_xml(self, task):
        relationships = {}
        id = 0
        if task.findall("pr:PredecessorLink", self.ns):
            for relationship in task.findall("pr:PredecessorLink", self.ns):
                relationships[id] = {
                    "PredecessorTask": relationship.find("pr:PredecessorUID", self.ns).text,
                    "Type": relationship.find("pr:Type", self.ns).text,
                }
                id += 1
        return relationships

    def parse_task_xml(self, project):
        for task in project.find("pr:Tasks", self.ns):
            task_id = task.find("pr:UID", self.ns).text
            task_index_level = task.find("pr:OutlineLevel", self.ns).text
            wbs_id = task.find("pr:WBS", self.ns).text
            relationships = self.parse_relationship_xml(task)
            outline_level = int(task.find("pr:OutlineLevel", self.ns).text)

            if outline_level != 0:
                parent_task = self.tasks[self.outline_parents[outline_level - 1]]
                parent_task["subtasks"].append(task_id)
            self.outline_level = outline_level
            self.outline_parents[outline_level] = task_id

            self.tasks[task_id] = {
                "Name": task.find("pr:Name", self.ns).text,
                "OutlineNumber": task.find("pr:OutlineNumber", self.ns).text,
                "OutlineLevel": outline_level,
                "Start": datetime.datetime.fromisoformat(task.find("pr:Start", self.ns).text),
                "Finish": datetime.datetime.fromisoformat(task.find("pr:Finish", self.ns).text),
                "Duration": ifcopenshell.util.date.ifc2datetime(task.find("pr:Duration", self.ns).text),
                "Priority": task.find("pr:Priority", self.ns).text,
                "CalendarUID": task.find("pr:CalendarUID", self.ns).text,
                "PredecessorTasks": relationships if relationships else None,
                "subtasks": [],
                "ifc": None,
            }

    def parse_calendar_xml(self, project):
        for calendar in project.find("pr:Calendars", self.ns).findall("pr:Calendar", self.ns):
            calendar_id = calendar.find("pr:UID", self.ns).text
            week_days = []
            for week_day in calendar.find("pr:WeekDays", self.ns).findall("pr:WeekDay", self.ns):
                working_times = []
                if week_day.find("pr:WorkingTimes", self.ns):
                    for working_time in week_day.find("pr:WorkingTimes", self.ns).findall("pr:WorkingTime", self.ns):
                        if working_time.find("pr:FromTime", self.ns) is None:
                            continue
                        working_times.append(
                            {
                                "Start": datetime.time.fromisoformat(working_time.find("pr:FromTime", self.ns).text),
                                "Finish": datetime.time.fromisoformat(working_time.find("pr:ToTime", self.ns).text),
                            }
                        )
                    week_days.append(
                        {
                            "DayType": week_day.find("pr:DayType", self.ns).text,
                            "WorkingTimes": working_times,
                            "ifc": None,
                        }
                    )
            exceptions = {}
            self.calendars[calendar_id] = {
                "Name": calendar.find("pr:Name", self.ns).text,
                "StandardWorkWeek": week_days,
            }