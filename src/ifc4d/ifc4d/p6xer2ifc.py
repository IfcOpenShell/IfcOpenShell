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
from datetime import datetime, timedelta, date
from common import ScheduleIfcGenerator


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
    
    RESOURCE_TYPES_MAPPING = {
        'RT_Labor': "LABOR",
        'RT_Mat': "MATERIAL",
        'RT_Equip': "EQUIPMENT"
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
        self.resources = {}
        
        
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
        ifcCreator.create_ifc()
       
    
    def parse_xer(self):
        self.model = Reader(self.xer)
        # for project in self.model.projects:
        #     if not self.project.get("Name"):
        self.project["Name"] = self.model.projects._projects[0].proj_short_name
        self.parse_calendar_xer()
        self.parse_wbs_xer()
        self.parse_activity_xer()
        self.parse_relationship_xer()
        self.parse_resource_xer()
        #work_schedule = self.create_work_schedule()
        #self.create_tasks(work_schedule)
        
            
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
        exceptions = {}
        for cal in self.model.calendars:
            standard_work_week = cal.working_hours
            except_lst = cal.exceptions
            for exception in except_lst:
                 month = exceptions.setdefault(exception.year, {}).setdefault(exception.month, {})
                 month.setdefault("FullDay", [])
                 month.setdefault("WorkTime", [])
                 exceptions[exception.year][exception.month]["FullDay"].append(exception.day)
                 
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
    

    def parse_resource_xer(self):
        for rsrc in self.model.resources:
            self.resources[rsrc.rsrc_id] = {
                "Name": rsrc.rsrc_name,
                "Code": rsrc.rsrc_short_name,
                "ParentObjectId": rsrc.parent_rsrc_id,
                "Type": self.RESOURCE_TYPES_MAPPING[rsrc.rsrc_type],
                "ifc": None,
                "rel": None,
            }
    

    

# TODO: add support for resources
# TODO: consider showing progress bar for better user experience
# TODO: support multiple projects in a single file
# TODO: prompt user to select activities and/or wbs nodes to import instead of the full project
