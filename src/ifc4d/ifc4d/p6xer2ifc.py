# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from xerparser.reader import Reader
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime, time, timedelta


class P6XER2Ifc():
    status_map = {
        "TK_NotStart": "Not Start",
        "TK_Complete": "Completed",
        "TK_Active": "Progress"
    }
    
    TASK_TYPE_MAP = {
        "TT_Task": "Task",
        "TT_Rsrc": "Resource Dependent Task",
        "TT_LOE": "Level of Effort",
        "TT_Mile": "Start Milestone",
        "TT_FinMile": "Finish Milestone",
        "TT_WBS": "WBS Summary"
    }
    
    RELATIONSHIP_TYPE_MAPPING = {
        "PR_SS": "START_START",
        "PR_FS": "FINISH_START",
        "PR_SF": "START_FINISH",
        "PR_FF": "FINISH_FINISH" 
    }
    
    def __init__(self):
        self.xer = None
        self.file = None
        self.model = None
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
        
        self.day_map2 = {
            '1': "Monday",
            '2': "Tuesday",
            '3': "Wednesday",
            '4': "Thursday",
            '5': "Friday",
            '6': "Saturday",
            '7': "Sunday",
        }
        
    
    def execute(self):
        self.parse_xer()
        self.create_ifc()
       
    
    def parse_xer(self):
        self.model = Reader(self.xer)
        # for project in self.model.projects:
        #     if not self.project.get("Name"):
        self.project["Name"] = self.model.projects._projects[0].proj_short_name
        print(self.project, type(self.model.projects._projects))
        self.parse_calendar_xer()
        self.parse_wbs_xer()
        self.parse_activity_xer()
        self.parse_relationship_xer()
        work_schedule = self.create_work_schedule()
        
            
    def parse_wbs_xer(self):
        for wbs in self.model.wbss:
            self.wbs[wbs.wbs_id] = {
                "Name": wbs.wbs_name,
                "Code": wbs.wbs_short_name,
                "ParentObjectId": wbs.parent_wbs_id,
                "ifc": None,
                "rel": None,
                "activities": [],
            }
        #print(self.wbs)
    
    def parse_calendar_xer(self):
        standard_work_week = []
        for cal in self.model.calendars:
            standard_work_week = []
            for k,v in cal.working_days.items(): #TODO: add work times
                standard_work_week.append({
                        "DayOfWeek": self.day_map2[k],
                        "WorkTimes": [{
                                        "Start": time(8, 0),
                                        "Finish": time(16, 0)
                                            }] if not v else [],
                        "ifc": None,
                })
            exceptions = {} #TODO: to be implemented 
            self.calendars[cal.clndr_id] = {
                "Name": cal.clndr_name,
                "Type": cal.clndr_type,
                "HoursPerDay": cal.day_hr_cnt,
                "StandardWorkWeek": standard_work_week,
                "HolidayOrExceptions": exceptions,
            }
    
    def parse_activity_xer(self):
        for activity in self.model.activities:
            activity_type = activity.task_type
            if activity_type == "TT_LOE":
                continue
            wbs_id = activity.wbs_id
            if wbs_id:
                self.wbs[wbs_id]["activities"].append(activity.task_id)
            else:
                self.root_activites.append(activity.task_id)
            self.activities[activity.task_id] = {
                "Name": activity.task_name,
                "Identification": activity.task_code,
                "StartDate": activity.start_date,
                "FinishDate": activity.end_date,
                "PlannedDuration": activity.target_drtn_hr_cnt,
                "Status": self.status_map[activity.status_code],
                "CalendarObjectId": activity.clndr_id,
                "ifc": None
            }
            
    def parse_relationship_xer(self):
        for rel in self.model.relations:
            predecessor = rel.pred_task_id
            successor = rel.task_id
            if predecessor not in self.activities or successor not in self.activities:
                continue
            self.relationships[rel.task_pred_id] = {
                "PredecessorActivity": predecessor,
                "SuccessorActivity": successor,
                "Type": self.RELATIONSHIP_TYPE_MAPPING[rel.pred_type],
                "Lag": rel.lag_hr_cnt,
            }
    

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
                "sequence.add_work_calendar", self.file, name=calendar["Name"]
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
        if not self.wbs.get(wbs["ParentObjectId"]):
            wbs["ParentObjectId"] = None
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
        #print(calendar, self.calendars)
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
                "ScheduleDuration": timedelta(
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
                attributes={"SequenceType": relationship["Type"]},
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

# TODO: working time need to be extracted from the xer not hard coded
# TODO: exceptions need to be implemented 
# TODO: add support for resources
# TODO: consider showing progress bar for better user experience
# TODO: support multiple projects in a single file
# TODO: prompt user to select activities and/or wbs nodes to import instead of the full project
