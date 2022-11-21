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


class MSP2Ifc:
    def __init__(self):
        self.xml = None
        self.file = None
        self.ns = None
        self.work_plan = None
        self.project = {}
        self.calendars = {}
        self.tasks = {}
        self.resources = {}
        self.RESOURCE_TYPES_MAPPING = {"1": "LABOR", "0": "MATERIAL", "2": None}

    def execute(self):
        self.parse_xml()
        self.create_ifc()

    def parse_xml(self):
        tree = ET.parse(self.xml)
        project = tree.getroot()
        self.ns = {"pr": project.tag[1:].partition("}")[0]}
        self.project["Name"] = project.findtext("pr:Name", namespaces=self.ns) or "Unnamed"
        self.project["CalendarUID"] = project.findtext("pr:CalendarUID", namespaces=self.ns) or None
        self.project["MinutesPerDay"] = project.findtext("pr:MinutesPerDay", namespaces=self.ns) or None
        self.outline_level = 0
        self.outline_parents = {}
        self.parse_task_xml(project)
        self.parse_calendar_xml(project)
        # TODO Doesn't do anything right now
        # self.parse_resources_xml(project)

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
        if self.project["MinutesPerDay"]:
            hours_per_day = int(self.project["MinutesPerDay"]) / 60
        else:
            hours_per_day = 8

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

            # Microsoft Project stores durations in terms of hours.
            duration = ifcopenshell.util.date.ifc2datetime(task.find("pr:Duration", self.ns).text)
            hours = duration.days * 24
            hours += duration.seconds / 60 / 60
            # Let's convert it into days, where days is the appropriate hours per day
            duration = timedelta(days=hours / float(hours_per_day))

            self.tasks[task_id] = {
                "Name": task.find("pr:Name", self.ns).text,
                "OutlineNumber": task.find("pr:OutlineNumber", self.ns).text,
                "OutlineLevel": outline_level,
                "Start": datetime.datetime.fromisoformat(task.find("pr:Start", self.ns).text),
                "Finish": datetime.datetime.fromisoformat(task.find("pr:Finish", self.ns).text),
                "Duration": duration,
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
            week_days_element = calendar.find("pr:WeekDays", self.ns)
            week_day_elements = week_days_element.findall("pr:WeekDay", self.ns) if week_days_element else []
            for week_day in week_day_elements:
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

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.run("sequence.add_work_plan", self.file)
        work_schedule = self.create_work_schedule()
        self.create_calendars()
        self.create_tasks(work_schedule)
        self.create_rel_sequences()

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.work_plan = self.file.create_entity("IfcWorkPlan")

    def create_tasks(self, work_schedule):
        for task_id in self.tasks:
            task = self.tasks[task_id]
            if task["OutlineLevel"] == 0:
                self.create_task(task, work_schedule=work_schedule)

    def create_work_schedule(self):
        return ifcopenshell.api.run(
            "sequence.add_work_schedule", self.file, name=self.project["Name"], work_plan=self.work_plan
        )

    def create_calendars(self):
        for calendar in self.calendars.values():
            calendar["ifc"] = ifcopenshell.api.run("sequence.add_work_calendar", self.file, name=calendar["Name"])
            self.process_working_week(calendar["StandardWorkWeek"], calendar["ifc"])

    def create_task(self, task, work_schedule=None, parent_task=None):
        task["ifc"] = ifcopenshell.api.run(
            "sequence.add_task",
            self.file,
            work_schedule=work_schedule if work_schedule else None,
            parent_task=parent_task["ifc"] if parent_task else None,
        )

        calendar = None
        if task["CalendarUID"] != "-1":
            calendar = self.calendars[task["CalendarUID"]]["ifc"]
        elif not parent_task and self.project["CalendarUID"]:
            calendar = self.calendars[self.project["CalendarUID"]]["ifc"]

        if calendar:
            ifcopenshell.api.run(
                "control.assign_control",
                self.file,
                **{
                    "relating_control": calendar,
                    "related_object": task["ifc"],
                },
            )

        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=task["ifc"],
            attributes={
                "Name": task["Name"],
                "Identification": task["OutlineNumber"],
                "IsMilestone": task["Start"] == task["Finish"],
            },
        )
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task["ifc"])
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleStart": task["Start"],
                "ScheduleFinish": task["Finish"],
                "DurationType": "WORKTIME" if task["Duration"] else None,
                "ScheduleDuration": task["Duration"] if task["Duration"] else None,
            },
        )
        for subtask_id in task["subtasks"]:
            self.create_task(self.tasks[subtask_id], parent_task=task)

    def process_working_week(self, week, calendar):
        day_map = {
            "1": 7, # Sunday
            "2": 1, # Monday
            "3": 2, # Tuesday
            "4": 3, # Wednesday
            "5": 4, # Thursday
            "6": 5, # Friday
            "7": 6, # Saturday
        }
        for day in week:
            if day["ifc"]:
                continue

            day["ifc"] = ifcopenshell.api.run(
                "sequence.add_work_time", self.file, work_calendar=calendar, time_type="WorkingTimes"
            )

            weekday_component = [day_map[day["DayType"]]]
            for day2 in week:
                if day["DayType"] == day2["DayType"]:
                    continue
                if day["WorkingTimes"] == day2["WorkingTimes"]:
                    weekday_component.append(day_map[day2["DayType"]])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            work_time_name = "Weekdays: {}".format(", ".join([str(c) for c in sorted(weekday_component)]))
            ifcopenshell.api.run(
                "sequence.edit_work_time",
                self.file,
                work_time=day["ifc"],
                attributes={"Name": work_time_name},
            )

            recurrence = ifcopenshell.api.run(
                "sequence.assign_recurrence_pattern", self.file, parent=day["ifc"], recurrence_type="WEEKLY"
            )
            ifcopenshell.api.run(
                "sequence.edit_recurrence_pattern",
                self.file,
                recurrence_pattern=recurrence,
                attributes={"WeekdayComponent": weekday_component},
            )
            for work_time in day["WorkingTimes"]:
                ifcopenshell.api.run(
                    "sequence.add_time_period",
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def create_rel_sequences(self):
        self.sequence_type_map = {
            "0": "FINISH_FINISH",
            "1": "FINISH_START",
            "2": "START_FINISH",
            "3": "START_START",
        }
        for task in self.tasks.values():
            if not task["PredecessorTasks"]:
                continue
            for predecessor in task["PredecessorTasks"].values():
                rel_sequence = ifcopenshell.api.run(
                    "sequence.assign_sequence",
                    self.file,
                    related_process=task["ifc"],
                    relating_process=self.tasks[predecessor["PredecessorTask"]]["ifc"],
                )
                if predecessor["Type"]:
                    ifcopenshell.api.run(
                        "sequence.edit_sequence",
                        self.file,
                        rel_sequence=rel_sequence,
                        attributes={"SequenceType": self.sequence_type_map[predecessor["Type"]]},
                    )

    def parse_resources_xml(self, project):
        resources_lst = project.find("pr:Resources", self.ns)
        resources = resources_lst.findall("pr:Resource", self.ns)
        # print("Resource text", resources[4].find("pr:Name", self.ns).text)
        for resource in resources:
            name = resource.find("pr:Name", self.ns)
            id = resource.find("pr:ID", self.ns).text
            if name is not None:
                name = name.text
            else:
                # print("- No Name")
                name = None
            self.resources[id] = {
                "Name": name,
                "Code": resource.find("pr:UID", self.ns).text,
                "ParentObjectId": None,
                "Type": self.RESOURCE_TYPES_MAPPING[resource.find("pr:Type", self.ns).text],
                "ifc": None,
                "rel": None,
            }
        print("Resource found", self.resources)
