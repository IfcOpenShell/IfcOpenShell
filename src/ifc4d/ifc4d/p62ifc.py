
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
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }

    def execute(self):
        self.parse_xml()
        self.create_ifc()

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
                "Type": relationship.find("pr:Type", self.ns).text,
                "Lag": relationship.find("pr:Lag", self.ns).text,
            }

    def get_wbs(self, wbs):
        return {"Name": wbs.find("pr:Name", self.ns).text, "subtasks": []}

    def create_ifc(self):
        if not self.file:
            self.file = self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.run("sequence.add_work_plan", self.file)
        work_schedule = self.create_work_schedule()
        self.create_calendars()
        self.create_tasks(work_schedule)
        self.create_rel_sequences()

    def create_work_schedule(self):
        return ifcopenshell.api.run(
            "sequence.add_work_schedule", self.file, name=self.project["Name"], work_plan=self.work_plan
        )

    def create_calendars(self):
        for calendar in self.calendars.values():
            calendar["ifc"] = ifcopenshell.api.run(
                "sequence.add_work_calendar", self.file, name=calendar["Name"], predefined_type=calendar["Type"]
            )
            self.process_working_week(calendar["StandardWorkWeek"], calendar["ifc"])
            self.process_exceptions(calendar["HolidayOrExceptions"], calendar["ifc"])

    def process_working_week(self, week, calendar):
        for day in week:
            if day["ifc"] or not day["WorkTimes"]:
                continue

            day["ifc"] = ifcopenshell.api.run(
                "sequence.add_work_time", self.file, work_calendar=calendar, time_type="WorkingTimes"
            )

            weekday_component = [self.day_map[day["DayOfWeek"]]]
            for day2 in week:
                if day["DayOfWeek"] == day2["DayOfWeek"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    weekday_component.append(self.day_map[day2["DayOfWeek"]])
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
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.run(
                    "sequence.add_time_period",
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def process_exceptions(self, exceptions, calendar):
        for year, year_data in exceptions.items():
            for month, month_data in year_data.items():
                if month_data["FullDay"]:
                    self.process_full_day_exceptions(year, month, month_data, calendar)
                if month_data["WorkTime"]:
                    self.process_work_time_exceptions(year, month, month_data, calendar)

    def process_full_day_exceptions(self, year, month, month_data, calendar):
        work_time = ifcopenshell.api.run(
            "sequence.add_work_time", self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        ifcopenshell.api.run(
            "sequence.edit_work_time",
            self.file,
            work_time=work_time,
            attributes={
                "Name": f"{year}-{month}",
                "Start": datetime.date(year, 1, 1),
                "Finish": datetime.date(year, 12, 31),
            },
        )
        recurrence = ifcopenshell.api.run(
            "sequence.assign_recurrence_pattern",
            self.file,
            parent=work_time,
            recurrence_type="YEARLY_BY_DAY_OF_MONTH",
        )
        ifcopenshell.api.run(
            "sequence.edit_recurrence_pattern",
            self.file,
            recurrence_pattern=recurrence,
            attributes={"DayComponent": month_data["FullDay"], "MonthComponent": [month]},
        )

    def process_work_time_exceptions(self, year, month, month_data, calendar):
        for day in month_data["WorkTime"]:
            if day["ifc"]:
                continue

            day["ifc"] = ifcopenshell.api.run(
                "sequence.add_work_time", self.file, work_calendar=calendar, time_type="ExceptionTimes"
            )

            day_component = [day["Day"]]
            for day2 in month_data["WorkTime"]:
                if day["Day"] == day2["Day"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    day_component.append(day2["Day"])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            ifcopenshell.api.run(
                "sequence.edit_work_time",
                self.file,
                work_time=day["ifc"],
                attributes={
                    "Name": "{}-{}-{}".format(year, month, ", ".join([str(d) for d in day_component])),
                    "Start": datetime.date(year, 1, 1),
                    "Finish": datetime.date(year, 12, 31),
                },
            )
            recurrence = ifcopenshell.api.run(
                "sequence.assign_recurrence_pattern",
                self.file,
                parent=day["ifc"],
                recurrence_type="YEARLY_BY_DAY_OF_MONTH",
            )
            ifcopenshell.api.run(
                "sequence.edit_recurrence_pattern",
                self.file,
                recurrence_pattern=recurrence,
                attributes={"DayComponent": day_component, "MonthComponent": [month]},
            )
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.run(
                    "sequence.add_time_period",
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def create_tasks(self, work_schedule):
        for wbs in self.wbs.values():
            self.create_task_from_wbs(wbs, work_schedule)
        for activity_id in self.root_activites:
            self.create_task_from_activity(self.activities[activity_id], None, work_schedule)

    def create_task_from_wbs(self, wbs, work_schedule):
        wbs["ifc"] = ifcopenshell.api.run(
            "sequence.add_task",
            self.file,
            work_schedule=None if wbs["ParentObjectId"] else work_schedule,
            parent_task=self.wbs[wbs["ParentObjectId"]]["ifc"] if wbs["ParentObjectId"] else None,
        )
        identification = wbs["Code"]
        if wbs["ParentObjectId"]:
            identification = self.wbs[wbs["ParentObjectId"]]["ifc"].Identification + "." + wbs["Code"]
        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=wbs["ifc"],
            attributes={"Name": wbs["Name"], "Identification": identification},
        )
        for activity_id in wbs["activities"]:
            self.create_task_from_activity(self.activities[activity_id], wbs, None)

    def create_task_from_activity(self, activity, wbs, work_schedule):
        activity["ifc"] = ifcopenshell.api.run(
            "sequence.add_task",
            self.file,
            work_schedule=None if wbs else work_schedule,
            parent_task=wbs["ifc"] if wbs else None,
        )
        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=activity["ifc"],
            attributes={
                "Name": activity["Name"],
                "Identification": activity["Identification"],
                "Status": activity["Status"],
                "IsMilestone": activity["StartDate"] == activity["FinishDate"],
                "PredefinedType": "CONSTRUCTION"
            },
        )
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=activity["ifc"])
        calendar = self.calendars[activity["CalendarObjectId"]]
        # Seems intermittently crashy - can we investigate for larger files?
        ifcopenshell.api.run(
            "control.assign_control",
            self.file,
            **{
                "relating_control": calendar["ifc"],
                "related_object": activity["ifc"],
            },
        )
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleStart": activity["StartDate"],
                "ScheduleFinish": activity["FinishDate"],
                "DurationType": "WORKTIME" if activity["PlannedDuration"] else None,
                "ScheduleDuration": datetime.timedelta(
                    days=float(activity["PlannedDuration"]) / float(calendar["HoursPerDay"])
                )
                or None
                if activity["PlannedDuration"]
                else None,
            },
        )

    def create_rel_sequences(self):
        self.sequence_type_map = {
            "Start to Start": "START_START",
            "Start to Finish": "START_FINISH",
            "Finish to Start": "FINISH_START",
            "Finish to Finish": "FINISH_FINISH",
        }
        for relationship in self.relationships.values():
            rel_sequence = ifcopenshell.api.run(
                "sequence.assign_sequence",
                self.file,
                relating_process=self.activities[relationship["PredecessorActivity"]]["ifc"],
                related_process=self.activities[relationship["SuccessorActivity"]]["ifc"],
            )
            ifcopenshell.api.run(
                "sequence.edit_sequence",
                self.file,
                rel_sequence=rel_sequence,
                attributes={"SequenceType": self.sequence_type_map[relationship["Type"]]},
            )
            lag = float(relationship["Lag"])
            if lag:
                calendar = self.calendars[self.activities[relationship["PredecessorActivity"]]["CalendarObjectId"]]
                ifcopenshell.api.run(
                    "sequence.assign_lag_time",
                    self.file,
                    rel_sequence=rel_sequence,
                    lag_value=datetime.timedelta(days=lag / float(calendar["HoursPerDay"])),
                    duration_type="WORKTIME",
                )

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.work_plan = self.file.create_entity("IfcWorkPlan")
