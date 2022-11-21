print("In module products __package__, __name__ ==", __package__)
print(__name__)
import sys

print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
sys.path.append(sys.path[0])

import sqlite3
import math
import datetime
from datetime import timedelta
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
from .wpattern import AstaCalendarWorkPattern
from .common import ScheduleIfcGenerator
import time


list_of_tables = [
    "BAR",
    "EXPANDED_TASK",
    "PERMANENT_RESOURCE",
    "CONSUMABLE_RESOURCE",
    "TASK",
    "PROJECT_SUMMARY",
    "WBS_ENTRY",
]


class PP2Ifc:
    def __init__(self):

        self.pp = None
        self.file = None
        self.work_plan = None
        self.project = {}
        self.calendars = {}
        self.wbs = {}
        self.root_activites = []
        self.activities = {}
        self.relationships = {}
        self.resources = {}
        self.output = None

        self.relationship_map = {0: "FINISH_START", 1: "FINISH_FINISH", 2: "START_START", 3: "START_FINISH"}

    def get_json(self, table_name):
        self.cur.execute("select * from " + table_name)
        r = [dict((self.cur.description[i][0], value) for i, value in enumerate(row)) for row in self.cur.fetchall()]
        return r

    def get_json_with_filter(self, table_name, attr_name, attr_value):
        self.cur.execute("select * from " + table_name + " where " + attr_name + " = " + str(attr_value))
        r = [dict((self.cur.description[i][0], value) for i, value in enumerate(row)) for row in self.cur.fetchall()]
        return r

    def execute(self):
        self.con = sqlite3.connect(self.pp)
        self.cur = self.con.cursor()
        self.parse_pp()
        settings = {
            "work_plan": self.work_plan,
            "project": self.project,
            "calendars": self.calendars,
            "wbs": self.wbs,
            "root_activities": self.root_activites,
            "activities": self.activities,
            "relationships": self.relationships,
            "resources": self.resources,
        }
        start = time.time()
        ifcCreator = ScheduleIfcGenerator(self.file, self.output, settings)
        end = time.time()

        ifcCreator.create_ifc()
        end2 = time.time()
        print("Parsing time is", end - start)
        print("IFC Creation took", end2 - end)
        print("Overall Time", end2 - start)
        # self.create_ifc()

    def parse_pp(self):

        project = self.get_json("PROJECT_SUMMARY")[0]
        self.project["Name"] = project["SHORT_NAME"]
        self.parse_calendar_pp()
        self.parse_bar()
        self.parse_relationship_pp(project)

    def parse_calendar_pp(self):
        calendars = self.get_json("CALENDAR")
        wp_data = self.get_json("WORK_PATTERN")
        work_types = self.get_json("EXCEPTIONN")
        work_type_ids = [wt["ID"] for wt in work_types if wt["EXCEPTION_TYPE"] == 0]

        for calendar in calendars:
            calendar_id = calendar["ID"]
            calendar_wp = calendar["DOMINANT_WORK_PATTERN"]
            wp_data = self.get_json_with_filter("WORK_PATTERN", "ID", calendar_wp)
            wp = AstaCalendarWorkPattern(wp_data[0]["SHIFTS"], work_type_ids)
            exceptions = {}
            timex = []
            for times in wp.dict_wp:
                work_times = timedelta(hours=0)
                for daily in times["WorkTimes"]:
                    fin = daily["Finish"]
                    strt = daily["Start"]
                    work_times += timedelta(hours=fin.hour, minutes=fin.minute) - timedelta(
                        hours=strt.hour, minutes=strt.minute
                    )
                timex.append(work_times.total_seconds() / (60 * 60))

            self.calendars[calendar_id] = {
                "Name": calendar["NAME"],
                "Type": "NOTDEFINED",
                "HoursPerDay": max(timex),
                "StandardWorkWeek": wp.dict_wp,
                "HolidayOrExceptions": exceptions,
            }
            # print(self.calendars[calendar_id])

    def parse_bar(self):
        bars = self.get_json("BAR")
        expanded_tasks = {t["BAR"]: t for t in self.get_json("EXPANDED_TASK")}
        tasks = {t["BAR"]: t for t in self.get_json("TASK")}
        milestones = {m["BAR"]: m for m in self.get_json("MILESTONE")}

        schedule_task = None

        bar_tasks = {}
        wbs_activities = {}

        for bar in bars:
            extra_type = None
            extra_data = None
            bar_id = None

            if bar["ID"] in expanded_tasks:
                extra_type = "EXPANDED_TASK"
                extra_data = expanded_tasks[bar["ID"]]
            elif bar["ID"] in tasks:
                extra_type = "TASK"
                extra_data = tasks[bar["ID"]]
            elif bar["ID"] in milestones:
                extra_type = "MILESTONE"
                extra_data = milestones[bar["ID"]]
            else:
                # Not sure where this might be the case
                continue

            name = bar["NAME"]
            if extra_data["NAME"]:
                name += f" - {extra_data['NAME']}"
            bar_tasks[extra_data["ID"]] = {"bar": bar, "extra_type": extra_type, "extra_data": extra_data}

            if extra_type == "EXPANDED_TASK":
                self.wbs[extra_data["ID"]] = {
                    "Name": name,
                    "Code": extra_data["ID"],
                    "ParentObjectId": bar["EXPANDED_TASK"] if bar["EXPANDED_TASK"] > 0 else None,
                    "ifc": None,
                    "rel": None,
                    "activities": [],
                }
            else:
                if "PLANNED_DURATION" in extra_data.keys():
                    activity_duration = float(
                        extra_data["PLANNED_DURATION"].split(",")[-2].replace("<", "").replace(">", "")
                    )
                elif "GIVEN_DURATION" in extra_data.keys():
                    activity_duration = float(
                        extra_data["GIVEN_DURATION"].split(",")[-2].replace("<", "").replace(">", "")
                    )
                else:
                    activity_duration = 0.0

                self.activities[extra_data["ID"]] = {
                    "Name": name,
                    "Identification": extra_data["ID"],
                    "StartDate": datetime.datetime.fromisoformat(extra_data["LINKABLE_START"]),
                    "FinishDate": datetime.datetime.fromisoformat(extra_data["LINKABLE_FINISH"]),
                    "PlannedDuration": activity_duration,
                    "Status": "PLANNED",
                    "CalendarObjectId": extra_data["CALENDAR"],
                    "ifc": None,
                }
                wbs_activities.setdefault(bar["EXPANDED_TASK"], []).append(extra_data["ID"])

        for wbs, activities in wbs_activities.items():
            self.wbs[wbs]["activities"] = activities

    def parse_relationship_pp(self, project):
        relations = self.get_json("LINK")
        # print(relations)
        for relationship in relations:
            predecessor = relationship["START_TASK"]
            successor = relationship["END_TASK"]
            if predecessor not in self.activities:
                print(f"Linked predecessor task {predecessor} cannot be found.")
                continue
            if successor not in self.activities:
                print(f"Linked successor task {successor} cannot be found.")
                continue
            self.relationships[relationship["ID"]] = {
                "PredecessorActivity": predecessor,
                "SuccessorActivity": successor,
                "Type": self.relationship_map[relationship["LINK_KIND"]],
                "Lag": float(relationship["END_LAG_TIME"].split(",")[-2].replace("<", "").replace(">", "")),
            }
