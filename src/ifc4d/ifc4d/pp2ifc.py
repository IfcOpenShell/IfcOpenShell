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
        'BAR',
        'EXPANDED_TASK',
        'PERMANENT_RESOURCE',
        'CONSUMABLE_RESOURCE',
        'TASK',
        'PROJECT_SUMMARY',
        'WBS_ENTRY'       
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
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }
        
        self.relationship_map = {
        0: "FINISH_START",
        1: "FINISH_FINISH",
        2: "START_START",
        3: "START_FINISH"
        }
        
    

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
            "work_plan":self.work_plan, 
            "project": self.project,
            "calendars": self.calendars,
            "wbs": self.wbs,
            "root_activities": self.root_activites,
            "activities": self.activities,
            "relationships": self.relationships,
            "resources": self.resources
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
        self.parse_wbs_pp()
        self.parse_activity_pp()
        self.parse_relationship_pp(project)

    def parse_calendar_pp(self):
        calendars = self.get_json("CALENDAR")
        wp_data = self.get_json("WORK_PATTERN")
        
        for calendar in calendars:
            calendar_id = calendar["ID"]
            calendar_wp = calendar["DOMINANT_WORK_PATTERN"]
            wp_data = self.get_json_with_filter("WORK_PATTERN", "ID", calendar_wp)
            print("wp_data", wp_data[0]['SHIFTS'])
            wp = AstaCalendarWorkPattern(wp_data[0]['SHIFTS'])
            print(wp.dict_wp)
            exceptions = {}
            timex = []
            for times in wp.dict_wp:
                work_times = timedelta(hours=0)
                for daily in times['WorkTimes']:
                    fin = daily['Finish']
                    strt = daily['Start']
                    work_times += timedelta(hours=fin.hour, minutes=fin.minute) - timedelta(hours=strt.hour, minutes=strt.minute)
                timex.append(work_times.total_seconds() /(60*60))

            self.calendars[calendar_id] = {
                "Name": calendar["NAME"],
                "Type": "NOTDEFINED",
                "HoursPerDay": max(timex),
                "StandardWorkWeek": wp.dict_wp,
                "HolidayOrExceptions": exceptions,
            }
            #print(self.calendars[calendar_id])

    def parse_wbs_pp(self):
        bars = self.get_json("BAR")
        extended_tasks = self.get_json("EXPANDED_TASK")
        
        for bar in bars:
            self.wbs[bar["ID"]] = {
                "Name": bar["NAME"],
                "Code": bar["ID"],
                "ParentObjectId": bar["EXPANDED_TASK"] if bar["EXPANDED_TASK"]> 0 else None,
                "ifc": None,
                "rel": None,
                "activities": [],
            }
        for bar in extended_tasks:
            self.wbs[bar["ID"]] = {
                "Name": bar["NAME"],
                "Code": bar["ID"],
                "ParentObjectId": bar["BAR"] if bar["BAR"]> 0 else None,
                "ifc": None,
                "rel": None,
                "activities": [],
            }
        #print(self.wbs)

    def parse_activity_pp(self):
        activities = self.get_json("TASK")
        milestones = self.get_json("MILESTONE")
        for activity in activities:
            activity_type = "TASK"
            activity_id = activity["ID"]
            wbs_id = activity["BAR"]
            if wbs_id:
                self.wbs[wbs_id]["activities"].append(activity_id)
            else:
                self.root_activites.append(activity_id)
            self.activities[activity_id] = {
                "Name": activity["NAME"],
                "Identification": activity["ID"],
                "StartDate": datetime.datetime.fromisoformat(activity["LINKABLE_START"]),
                "FinishDate": datetime.datetime.fromisoformat(activity["LINKABLE_FINISH"]),
                "PlannedDuration": float(activity["PLANNED_DURATION"].split(",")[-2].replace("<","").replace(">","") ),
                "Status": "PLANNED",
                "CalendarObjectId": activity["CALENDAR"],
                "ifc": None,
            }
            
        for activity in milestones:
            activity_type = "MILESTONE"
            activity_id = activity["ID"]
            wbs_id = activity["BAR"]
            if wbs_id:
                self.wbs[wbs_id]["activities"].append(activity_id)
            else:
                self.root_activites.append(activity_id)
            self.activities[activity_id] = {
                "Name": activity["NAME"],
                "Identification": activity["ID"],
                "StartDate": datetime.datetime.fromisoformat(activity["LINKABLE_START"]),
                "FinishDate": datetime.datetime.fromisoformat(activity["LINKABLE_FINISH"]),
                "PlannedDuration": 0.0,
                "Status": "PLANNED",
                "CalendarObjectId": activity["CALENDAR"],
                "ifc": None,
            }
            #print("***ACTIVITIES", self.activities[activity_id])

    def parse_relationship_pp(self, project):
        relations = self.get_json('LINK')
        for relationship in relations:
            predecessor = relationship['START_TASK']
            successor = relationship['END_TASK']
            if predecessor not in self.activities or successor not in self.activities:
                print("!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!")
                print(predecessor, successor)
                continue
            self.relationships[relationship["ID"]] = {
                "PredecessorActivity": predecessor,
                "SuccessorActivity": successor,
                "Type": self.relationship_map[relationship['LINK_KIND']],
                "Lag": float(relationship['END_LAG_TIME'].split(",")[-2].replace("<","").replace(">","")),
            }
