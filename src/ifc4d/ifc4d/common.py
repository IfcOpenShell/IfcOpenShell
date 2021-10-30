from xerparser.reader import Reader
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime, timedelta, date


class ScheduleIfcGenerator:
    
    def __init__(self, file, settings):
        self.file = file
        self.work_plan = settings['work_plan']
        self.project = settings['project']
        self.calendars = settings['calendars']
        self.wbs = settings['wbs']
        self.root_activites = settings['root_activities']
        self.activities = settings['activities']
        self.relationships = settings['relationships']
        self.resources = settings['resources']
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
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
        self.create_resources()

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
            self.process_exceptions(calendar.get("HolidayOrExceptions"), calendar["ifc"])

    def process_working_week(self, week, calendar):
        for day in week:
            if day["ifc"] or not day.get("WorkTimes"):
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
        if exceptions:
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
                "Start": date(year, 1, 1),
                "Finish": date(year, 12, 31),
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
                    "Start": date(year, 1, 1),
                    "Finish": date(year, 12, 31),
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
            if self.wbs[wbs["ParentObjectId"]]["ifc"]:
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
                    lag_value=timedelta(days=lag / float(calendar["HoursPerDay"])),
                    duration_type="WORKTIME",
                )
                
                
    def create_resources(self):
        # print("Resources", self.resources)
        if self.resources:
            for id, resource in self.resources.items():
                
                parent = self.resources.get(resource.get("ParentObjectId"))
                if parent:
                    if not parent.get("ifc"):
                        parent["ifc"] = ifcopenshell.api.run(
                            "resource.add_resource",
                            self.file,
                            **{"ifc_class": "IfcCrewResource",
                            "name": parent['Name']}
                        )
                if parent:
                    resource["ifc"] = ifcopenshell.api.run(
                    "resource.add_resource",
                    self.file,
                    **{"parent_resource": parent["ifc"] if parent else None, 
                    "ifc_class": "IfcCrewResource",
                    "name": resource['Name']
                    }
                )
                else:
                    resource["ifc"] = ifcopenshell.api.run(
                    "resource.add_resource",
                    self.file,
                    **{ "ifc_class": "IfcCrewResource",
                    "name": resource['Name']
                    }
                )
            print(self.resources)

            

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.work_plan = self.file.create_entity("IfcWorkPlan")
