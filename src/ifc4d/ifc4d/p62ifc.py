
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

import math
import datetime
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import xml.etree.ElementTree as ET
from common import ScheduleIfcGenerator

class P62Ifc:
    def __init__(self):
        self.xml = None
        self.file = None
        self.work_plan = None
        self.project = {}
        self.calendars = {}
        self.wbs = {}
        self.root_activites = []
        self.activities = {}
        self.relationships = {}
        self.resources = {}
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }
        self.sequence_type_map = {
            "Start to Start": "START_START",
            "Start to Finish": "START_FINISH",
            "Finish to Start": "FINISH_START",
            "Finish to Finish": "FINISH_FINISH",
        }
        self.RESOURCE_TYPES_MAPPING = {
            'Labor': "LABOR",
            'Mat': "MATERIAL",
            'Equip': "EQUIPMENT"
        }

    def execute(self):
        import time

        start = time.time()
        print("Started")
        self.parse_xml()
        settings = {
            "work_plan":self.work_plan, 
            "project": self.project,
            "calendars": self.calendars,
            "wbs": self.wbs,
            "root_activities": self.root_activites,
            "activities": self.activities,
            "relationships": self.relationships,
            "resources": self.resources
        }
        ifcCreator = ScheduleIfcGenerator(self.file, settings)
        end = time.time()
        
        ifcCreator.create_ifc()
        end2 = time.time()
        print("Parsing time is", end - start)
        print("IFC Creation took", end2 - end)
        print("Overall Time", end2 - start)

    def parse_xml(self):
        tree = ET.parse(self.xml)
        root = tree.getroot()
        self.ns = {"pr": root.tag[1:].partition("}")[0]}
        project = root.find("pr:Project", self.ns)
        self.project["Name"] = project.find("pr:Name", self.ns).text
        self.parse_calendar_xml(root)
        self.parse_calendar_xml(project)
        self.parse_wbs_xml(project)
        self.parse_activity_xml(project)
        self.parse_relationship_xml(project)
        self.parse_resources_xml(root)

    def parse_calendar_xml(self, project):
        for calendar in project.findall("pr:Calendar", self.ns):
            calendar_id = calendar.find("pr:ObjectId", self.ns).text
            standard_work_week = []
            for standard_work_hour in calendar.find("pr:StandardWorkWeek", self.ns).findall(
                "pr:StandardWorkHours", self.ns
            ):
                work_times = []
                for work_time in standard_work_hour.findall("pr:WorkTime", self.ns):
                    if work_time.find("pr:Start", self.ns) is None:
                        continue
                    work_times.append(
                        {
                            "Start": datetime.time.fromisoformat(work_time.find("pr:Start", self.ns).text),
                            "Finish": datetime.time.fromisoformat(work_time.find("pr:Finish", self.ns).text),
                        }
                    )
                standard_work_week.append(
                    {
                        "DayOfWeek": standard_work_hour.find("pr:DayOfWeek", self.ns).text,
                        "WorkTimes": work_times,
                        "ifc": None,
                    }
                )
            exceptions = {}
            holiday_or_exceptions = calendar.find("pr:HolidayOrExceptions", self.ns)
            holiday_or_exception = []
            if holiday_or_exceptions is not None:
                holiday_or_exception = holiday_or_exceptions.findall("pr:HolidayOrException", self.ns)
            for exception in holiday_or_exception:
                d = datetime.datetime.fromisoformat(exception.find("pr:Date", self.ns).text).date()
                month = exceptions.setdefault(d.year, {}).setdefault(d.month, {})
                month.setdefault("FullDay", [])
                month.setdefault("WorkTime", [])
                work_times = []
                for work_time in exception.findall("pr:WorkTime", self.ns):
                    if work_time.find("pr:Start", self.ns) is None:
                        continue
                    work_times.append(
                        {
                            "Start": datetime.time.fromisoformat(work_time.find("pr:Start", self.ns).text),
                            "Finish": datetime.time.fromisoformat(work_time.find("pr:Finish", self.ns).text),
                        }
                    )
                if work_times:
                    exceptions[d.year][d.month]["WorkTime"].append({"Day": d.day, "WorkTimes": work_times, "ifc": None})
                else:
                    exceptions[d.year][d.month]["FullDay"].append(d.day)
            self.calendars[calendar_id] = {
                "Name": calendar.find("pr:Name", self.ns).text,
                "Type": calendar.find("pr:Type", self.ns).text,
                "HoursPerDay": calendar.find("pr:HoursPerDay", self.ns).text,
                "StandardWorkWeek": standard_work_week,
                "HolidayOrExceptions": exceptions,
            }

    def parse_wbs_xml(self, project):
        for wbs in project.findall("pr:WBS", self.ns):
            self.wbs[wbs.find("pr:ObjectId", self.ns).text] = {
                "Name": wbs.find("pr:Name", self.ns).text,
                "Code": wbs.find("pr:Code", self.ns).text,
                "ParentObjectId": wbs.find("pr:ParentObjectId", self.ns).text,
                "ifc": None,
                "rel": None,
                "activities": [],
            }

    def parse_activity_xml(self, project):
        for activity in project.findall("pr:Activity", self.ns):
            activity_type = activity.find("pr:Type", self.ns).text
            if activity_type == "Level of Effort":
                continue
            activity_id = activity.find("pr:ObjectId", self.ns).text
            wbs_id = activity.find("pr:WBSObjectId", self.ns).text
            if wbs_id:
                self.wbs[wbs_id]["activities"].append(activity_id)
            else:
                self.root_activites.append(activity_id)
            self.activities[activity_id] = {
                "Name": activity.find("pr:Name", self.ns).text,
                "Identification": activity.find("pr:Id", self.ns).text,
                "StartDate": datetime.datetime.fromisoformat(activity.find("pr:StartDate", self.ns).text),
                "FinishDate": datetime.datetime.fromisoformat(activity.find("pr:FinishDate", self.ns).text),
                "PlannedDuration": activity.find("pr:PlannedDuration", self.ns).text,
                "Status": activity.find("pr:Status", self.ns).text,
                "CalendarObjectId": activity.find("pr:CalendarObjectId", self.ns).text,
                "ifc": None,
            }

    def parse_relationship_xml(self, project):
        for relationship in project.findall("pr:Relationship", self.ns):
            predecessor = relationship.find("pr:PredecessorActivityObjectId", self.ns).text
            successor = relationship.find("pr:SuccessorActivityObjectId", self.ns).text
            if predecessor not in self.activities or successor not in self.activities:
                continue
            self.relationships[relationship.find("pr:ObjectId", self.ns).text] = {
                "PredecessorActivity": predecessor,
                "SuccessorActivity": successor,
                "Type": self.sequence_type_map[relationship.find("pr:Type", self.ns).text],
                "Lag": relationship.find("pr:Lag", self.ns).text,
            }

    def get_wbs(self, wbs):
        return {"Name": wbs.find("pr:Name", self.ns).text, "subtasks": []}
    
    
    def parse_resources_xml(self, project):
        resources = project.findall("pr:Resource", self.ns)
        for resource in resources:
            id = resource.find("pr:ObjectId", self.ns).text
            self.resources[id] = {
                "Name": resource.find("pr:Name", self.ns).text,
                "Code": resource.find("pr:Id", self.ns).text,
                "ParentObjectId": resource.find("pr:ParentObjectId", self.ns).text,
                "Type": self.RESOURCE_TYPES_MAPPING[resource.find("pr:ResourceType", self.ns).text],
                "ifc": None,
                "rel": None,
            }
        print("Resource found", self.resources)
            