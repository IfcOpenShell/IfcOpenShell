# Ifc4D - IFC scheduling utility
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import xml.etree.ElementTree as ET

from .common import ScheduleIfcGenerator

# P6 declares its user-defined fields once at the root and then references them
# by ObjectId from each activity, so the declaration is the only place the type
# is known. Each entry is the element P6 carries the value in, and the IFC type
# it becomes. Text maps to IfcLabel rather than IfcText: these are short tags
# and names — a planner, a responsible party, a work front — and IfcText means
# long-form prose.
# The third element coerces the XML text: IFC's numeric simple types reject a
# string outright ("Attribute not set"), and the value element carries text
# whatever the declared type says.
UDF_DATA_TYPES = {
    "Text": ("TextValue", "IfcLabel", str),
    "Double": ("DoubleValue", "IfcReal", float),
    "Integer": ("IntegerValue", "IfcInteger", int),
    "Cost": ("CostValue", "IfcMonetaryMeasure", float),
    "Indicator": ("IndicatorValue", "IfcLabel", str),
    "Start Date": ("StartDateValue", "IfcDateTime", str),
    "Finish Date": ("FinishDateValue", "IfcDateTime", str),
}


class P62Ifc:
    def __init__(self):
        self.xml = None
        self.file = None
        self.work_plan = None
        self.project = {}
        self.default_calendar_id = None
        self.calendars = {}
        self.wbs = {}
        self.udf_types = {}
        self.code_types = {}
        self.code_values = {}
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
        self.sequence_type_map = {
            "Start to Start": "START_START",
            "Start to Finish": "START_FINISH",
            "Finish to Start": "FINISH_START",
            "Finish to Finish": "FINISH_FINISH",
        }
        self.resource_type_map = {
            "Labor": "LABOR",
            "Mat": "MATERIAL",
            "Equip": "EQUIPMENT",
            # https://www.primaverascheduling.com/category/primavera-resources/
            "Nonlabor": "EQUIPMENT",
        }

    def execute(self):
        import time

        start = time.time()
        print("Started")
        self.parse_xml()
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
        ifcCreator = ScheduleIfcGenerator(self.file, self.output, settings)
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
        # findtext needs the namespace map too — without it the "pr:" prefix
        # resolves to nothing, every schedule came out named "Unnamed", and that
        # is the string a viewer puts in its header.
        self.project["Name"] = project.findtext("pr:Name", namespaces=self.ns) or "Unnamed"
        self.default_calendar_id = project.findtext("pr:ActivityDefaultCalendarObjectId", namespaces=self.ns)
        self.parse_calendar_xml(root)
        self.parse_calendar_xml(project)
        self.parse_udf_type_xml(root)
        self.parse_code_type_xml(root)
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

    def parse_udf_type_xml(self, root):
        """The declarations for P6's user-defined fields.

        Only Activity fields are read. P6 also allows them on projects,
        resources and WBS nodes, and those would need somewhere else to land.
        A type this importer has no mapping for is skipped rather than guessed
        at, because the value element it would be carried in is not knowable
        from the value itself.
        """
        for udf_type in root.findall("pr:UDFType", self.ns):
            if udf_type.findtext("pr:SubjectArea", namespaces=self.ns) != "Activity":
                continue
            data_type = udf_type.findtext("pr:DataType", namespaces=self.ns)
            if data_type not in UDF_DATA_TYPES:
                continue
            self.udf_types[udf_type.findtext("pr:ObjectId", namespaces=self.ns)] = {
                "Title": udf_type.findtext("pr:Title", namespaces=self.ns),
                "DataType": data_type,
            }

    def parse_udfs(self, activity):
        """This activity's user-defined fields, as {Title: (ifc_type, value)}."""
        udfs = {}
        for udf in activity.findall("pr:UDF", self.ns):
            declared = self.udf_types.get(udf.findtext("pr:TypeObjectId", namespaces=self.ns))
            if not declared:
                continue
            value_tag, ifc_type, coerce = UDF_DATA_TYPES[declared["DataType"]]
            value = udf.findtext(f"pr:{value_tag}", namespaces=self.ns)
            if value is None or value == "":
                continue
            try:
                value = coerce(value)
            except (TypeError, ValueError):
                # A value that does not match its own declared type is one bad
                # field, not a reason to lose the whole programme.
                continue
            udfs[declared["Title"]] = (ifc_type, value)
        return udfs

    def parse_code_type_xml(self, root):
        """Activity code types and their values, both keyed by ObjectId.

        Codes are a two-table reference like everything else in a P6 export: an
        activity carries <Code TypeObjectId ValueObjectId>, and the readable
        name and value live up here.
        """
        for code_type in root.findall("pr:ActivityCodeType", self.ns):
            self.code_types[code_type.findtext("pr:ObjectId", namespaces=self.ns)] = (
                code_type.findtext("pr:Name", namespaces=self.ns)
            )
        for code in root.findall("pr:ActivityCode", self.ns):
            self.code_values[code.findtext("pr:ObjectId", namespaces=self.ns)] = (
                code.findtext("pr:CodeValue", namespaces=self.ns),
                code.findtext("pr:Description", namespaces=self.ns) or "",
            )

    def parse_codes(self, activity):
        """This activity's assigned activity codes, as {type: (value, description)}."""
        codes = {}
        for code in activity.findall("pr:Code", self.ns):
            name = self.code_types.get(code.findtext("pr:TypeObjectId", namespaces=self.ns))
            assigned = self.code_values.get(code.findtext("pr:ValueObjectId", namespaces=self.ns))
            if name and assigned and assigned[0]:
                codes[name] = assigned
        return codes

    def parse_wbs_xml(self, project):
        for wbs in project.findall("pr:WBS", self.ns):
            self.wbs[wbs.find("pr:ObjectId", self.ns).text] = {
                "Name": wbs.find("pr:Name", self.ns).text,
                "Code": wbs.find("pr:Code", self.ns).text,
                "ParentObjectId": wbs.find("pr:ParentObjectId", self.ns).text,
                # P6's own ordering of siblings, which is NOT the order the
                # export lists them in. It is the only thing that reproduces the
                # breakdown a planner recognises, and IfcRelNests preserves it
                # for free because RelatedObjects is an ordered LIST — provided
                # the tasks are created in this order in the first place.
                "SequenceNumber": self.parse_float(wbs, "SequenceNumber") or 0,
                "ifc": None,
                "rel": None,
                "activities": [],
            }

    def parse_activity_xml(self, project):
        for activity in project.findall("pr:Activity", self.ns):
            activity_type = activity.find("pr:Type", self.ns).text
            activity_id = activity.find("pr:ObjectId", self.ns).text
            wbs_id = activity.find("pr:WBSObjectId", self.ns).text
            if wbs_id:
                self.wbs[wbs_id]["activities"].append(activity_id)
            else:
                self.root_activites.append(activity_id)
            # CalendarObjectId is optional in the P6 schema: an activity without one
            # inherits the project's ActivityDefaultCalendarObjectId.
            calendar_id = activity.findtext("pr:CalendarObjectId", namespaces=self.ns)
            self.activities[activity_id] = {
                "Name": activity.find("pr:Name", self.ns).text,
                "Identification": activity.find("pr:Id", self.ns).text,
                "StartDate": datetime.datetime.fromisoformat(activity.find("pr:StartDate", self.ns).text),
                "FinishDate": datetime.datetime.fromisoformat(activity.find("pr:FinishDate", self.ns).text),
                "PlannedDuration": activity.find("pr:PlannedDuration", self.ns).text,
                "Status": activity.find("pr:Status", self.ns).text,
                "CalendarObjectId": calendar_id or self.default_calendar_id,
                "Type": activity_type,
                "UDFs": self.parse_udfs(activity),
                "Codes": self.parse_codes(activity),
                # StartDate/FinishDate above are P6's CURRENT dates, which is
                # the live plan — P6 re-plans as actuals land, so on a started
                # activity the current start is the actual start. That is why
                # they, and not PlannedStartDate, map to ScheduleStart/Finish.
                # The actuals are carried separately so the fact that a date is
                # recorded rather than forecast is not lost.
                "ActualStartDate": self.parse_date(activity, "ActualStartDate"),
                "ActualFinishDate": self.parse_date(activity, "ActualFinishDate"),
                "EarlyStartDate": self.parse_date(activity, "EarlyStartDate"),
                "EarlyFinishDate": self.parse_date(activity, "EarlyFinishDate"),
                "LateStartDate": self.parse_date(activity, "LateStartDate"),
                "LateFinishDate": self.parse_date(activity, "LateFinishDate"),
                "TotalFloat": self.parse_float(activity, "TotalFloat"),
                "FreeFloat": self.parse_float(activity, "FreeFloat"),
                # P6 stores this as a 0..1 fraction, which is already what
                # IfcPositiveRatioMeasure wants.
                "PercentComplete": self.parse_float(activity, "PercentComplete"),
                "ifc": None,
            }

    def parse_date(self, activity, tag):
        text = activity.findtext(f"pr:{tag}", namespaces=self.ns)
        if not text:
            return None
        try:
            return datetime.datetime.fromisoformat(text)
        except ValueError:
            return None

    def parse_float(self, activity, tag):
        text = activity.findtext(f"pr:{tag}", namespaces=self.ns)
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

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
                "Type": self.resource_type_map[resource.find("pr:ResourceType", self.ns).text],
                "ifc": None,
                "rel": None,
            }
        print("Resource found", self.resources)
