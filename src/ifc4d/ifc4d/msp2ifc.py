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

"""Microsoft Project XML in, an IFC4 work schedule out.

    converter = MSP2Ifc()
    converter.xml = "programme.xml"
    converter.output = "programme.ifc"
    converter.execute()

The parse is MSP-specific; everything from the parsed programme onwards is
ScheduleIfcGenerator, shared with the P6 and Powerproject importers, so a
schedule reads the same whichever tool it came out of.

Two things about MS Project need saying, because they are what the shape of
this module is for.

The first is that MS Project has no work breakdown structure as a thing of its
own. It has one flat task list and an OutlineLevel column, and a task with
anything indented under it is a summary — its dates and duration are rolled up
from its children rather than planned. Those become IfcTasks without an
IfcTaskTime, the same as a P6 WBS node, and the leaves below them become the
activities. That is what makes "has this task an IfcTaskTime" a usable test for
"is this real work" in a file this importer wrote.

The second is that summaries and leaves are interleaved. A P6 WBS node holds
its child nodes and its activities in separate collections, so their relative
order is not a question anyone can ask; in MS Project a planner can put a
summary between two ordinary tasks and expects it to stay there. So the tree is
walked here in the order the export lists it, rather than through the
generator's create_tasks, which sorts nodes ahead of activities.
"""

from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET

import ifcopenshell.api.pset
import ifcopenshell.api.sequence
import ifcopenshell.guid
import ifcopenshell.util.date

from .common import ScheduleIfcGenerator

# MS Project counts weekdays from Sunday. IFC counts from Monday, but the
# generator takes the day by name, so the names are all that is needed here.
DAY_TYPES = {
    "1": "Sunday",
    "2": "Monday",
    "3": "Tuesday",
    "4": "Wednesday",
    "5": "Thursday",
    "6": "Friday",
    "7": "Saturday",
}

# https://learn.microsoft.com/en-us/office-project/xml-data-interchange/type-element-predecessorlink
SEQUENCE_TYPES = {
    "0": "FINISH_FINISH",
    "1": "FINISH_START",
    "2": "START_FINISH",
    "3": "START_START",
}

# A lag is normally a length of time, expressed in tenths of a minute whatever
# unit the LagFormat says it is displayed in. These two formats are the
# exception: the lag is a percentage of the predecessor's duration, which is
# not a duration and cannot be converted into one without the predecessor.
# https://learn.microsoft.com/en-us/office-project/xml-data-interchange/lagformat-element-predecessorlink
PERCENT_LAG_FORMATS = {"19", "20"}

TENTHS_OF_A_MINUTE_PER_HOUR = 600


class MSPIfcGenerator(ScheduleIfcGenerator):
    """ScheduleIfcGenerator, with MS Project's flat outline in place of a WBS."""

    udf_pset_name = "MSP_ExtendedAttribute"

    def __init__(self, file, output, settings):
        super().__init__(file, output, settings)
        # uid -> the uids indented directly under it, in the order the export
        # lists them, summaries and leaves together.
        self.children = settings["children"]
        self.roots = settings["roots"]
        self.default_hours_per_day = settings["hours_per_day"]

    def create_tasks(self, work_schedule):
        for uid in self.roots:
            self.create_node(uid, None, work_schedule)

    def create_node(self, uid, parent, work_schedule):
        """One outline row, and everything indented under it."""
        if uid not in self.wbs:
            self.create_task_from_activity(self.activities[uid], parent, work_schedule)
            return

        wbs = self.wbs[uid]
        wbs["ifc"] = ifcopenshell.api.sequence.add_task(
            self.file,
            work_schedule=None if parent else work_schedule,
            parent_task=parent["ifc"] if parent else None,
        )
        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=wbs["ifc"],
            # MS Project's OutlineNumber is already the full dotted path, so
            # unlike P6's WBS Code it needs no assembling from its ancestors.
            attributes={"Name": wbs["Name"], "Identification": str(wbs["Code"])},
        )
        # A summary task's dates are a roll-up and are dropped, but its custom
        # fields are not — a planner fills those in on a summary row as readily
        # as on a leaf, and nothing else in the file carries them.
        self.create_udf_pset(wbs)
        for child in self.children.get(uid, []):
            self.create_node(child, wbs, None)

    def create_task_from_activity(self, activity, wbs, work_schedule):
        super().create_task_from_activity(activity, wbs, work_schedule)
        columns = activity.get("OptionalColumns")
        if columns:
            pset = ifcopenshell.api.pset.add_pset(self.file, product=activity["ifc"], name="Pset_MSP_Task")
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=columns)

    def create_rel_sequences(self):
        """The links, including any that hang off a summary task.

        The generator's own resolves both ends against the activities, which
        is safe in P6 where a WBS node cannot be one. MS Project lets a planner
        link a summary, and IFC is content either way — IfcRelSequence relates
        two IfcProcesses and does not care whether either has a time.
        """
        for relationship in self.relationships.values():
            predecessor = self.task_for(relationship["PredecessorActivity"])
            successor = self.task_for(relationship["SuccessorActivity"])
            if predecessor is None or successor is None:
                continue

            sequence_type = relationship["Type"]
            rel_sequence = next(
                (
                    rel
                    for rel in successor.IsSuccessorFrom or []
                    if rel.RelatingProcess == predecessor and rel.SequenceType == sequence_type
                ),
                None,
            )
            if rel_sequence is None:
                rel_sequence = self.file.create_entity(
                    "IfcRelSequence",
                    GlobalId=ifcopenshell.guid.new(),
                    RelatingProcess=predecessor,
                    RelatedProcess=successor,
                    SequenceType=sequence_type,
                )
            if relationship["Lag"]:
                ifcopenshell.api.sequence.assign_lag_time(
                    self.file,
                    rel_sequence=rel_sequence,
                    lag_value=datetime.timedelta(days=relationship["Lag"] / self.hours_per_day(predecessor)),
                    duration_type="WORKTIME",
                )

    def task_for(self, uid):
        if uid in self.activities:
            return self.activities[uid]["ifc"]
        if uid in self.wbs:
            return self.wbs[uid]["ifc"]
        return None

    def hours_per_day(self, task):
        """The working day a lag against this task is counted in."""
        for rel in task.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkCalendar"):
                calendar = self.calendars.get(rel.RelatingControl.Identification)
                if calendar and calendar["HoursPerDay"]:
                    return float(calendar["HoursPerDay"])
        return float(self.default_hours_per_day)


class MSP2Ifc:
    def __init__(self, optionalColumns: list[str] = []):
        self.xml = None
        self.file = None
        self.output = None
        self.ns = None
        self.work_plan = None
        self.project = {}
        self.calendars = {}
        self.wbs = {}
        self.activities = {}
        self.root_activities = []
        self.children = {}
        self.roots = []
        self.relationships = {}
        self.resources = {}
        self.extended_attributes = {}
        self.hours_per_day = 8.0
        # Extra Task elements to copy onto a Pset_MSP_Task, by tag name. "all"
        # as the only entry takes every tag the first task carries.
        self.optionalColumns = optionalColumns
        self.RESOURCE_TYPES_MAPPING = {"1": "LABOR", "0": "MATERIAL", "2": None}

    def execute(self):
        self.parse_xml()
        settings = {
            "work_plan": self.work_plan,
            "project": self.project,
            "calendars": self.calendars,
            "wbs": self.wbs,
            "root_activities": self.root_activities,
            "activities": self.activities,
            "relationships": self.relationships,
            "resources": self.resources,
            "children": self.children,
            "roots": self.roots,
            "hours_per_day": self.hours_per_day,
        }
        MSPIfcGenerator(self.file, self.output, settings).create_ifc()

    # -- parsing ------------------------------------------------------------

    def parse_xml(self):
        tree = ET.parse(self.xml)
        project = tree.getroot()
        self.ns = {"pr": project.tag[1:].partition("}")[0]}

        # <Name> is the file the export came from; <Title> is what the planner
        # called the programme, and is the string a viewer puts in its header.
        self.project["Name"] = (
            self.text(project, "Title") or self.text(project, "Name") or "Unnamed"
        )
        self.project["CalendarUID"] = self.text(project, "CalendarUID")
        minutes_per_day = self.text(project, "MinutesPerDay")
        self.project["MinutesPerDay"] = minutes_per_day
        if minutes_per_day:
            self.hours_per_day = int(minutes_per_day) / 60

        self.parse_calendar_xml(project)
        self.parse_extended_attribute_types(project)
        self.parse_task_xml(project)
        self.parse_resources_xml(project)

    def text(self, element, tag):
        if element is None:
            return None
        return element.findtext(f"pr:{tag}", namespaces=self.ns)

    def parse_date(self, element, tag):
        """A date, or None where MS Project means "not set".

        Unset dates are usually omitted, but an export may carry "NA" or the
        1970-ish sentinel instead, and neither is a date anyone wants written
        into a schedule.
        """
        value = self.text(element, tag)
        if not value or value == "NA":
            return None
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            return None

    def parse_hours(self, element, tag):
        """A span MS Project states in tenths of a minute, as hours."""
        value = self.text(element, tag)
        if value is None or value == "":
            return None
        try:
            return float(value) / TENTHS_OF_A_MINUTE_PER_HOUR
        except ValueError:
            return None

    def parse_duration_hours(self, element, tag):
        """A Duration element, as a number of hours.

        Written as an ISO 8601 duration whose largest unit is the hour, so
        PT1976H0M0S — 247 eight hour days — rather than anything with days in
        it. isodate normalises that into days and seconds regardless.
        """
        value = self.text(element, tag)
        if not value:
            return None
        try:
            duration = ifcopenshell.util.date.ifc2datetime(value)
        except Exception:
            return None
        return duration.days * 24 + duration.seconds / 3600

    def parse_extended_attribute_types(self, project):
        """The custom column declarations, FieldID -> the name to file it under.

        A planner who renames Text1 to "Zone" gets an Alias; one who does not
        leaves the export saying Text1, and Text1 is then the only name there
        is to use.
        """
        declarations = project.find("pr:ExtendedAttributes", self.ns)
        for declaration in declarations.findall("pr:ExtendedAttribute", self.ns) if declarations is not None else []:
            field_id = self.text(declaration, "FieldID")
            name = self.text(declaration, "Alias") or self.text(declaration, "FieldName")
            if field_id and name:
                self.extended_attributes[field_id] = name

    def parse_extended_attributes(self, task):
        """This task's custom field values, as {name: (ifc_type, value)}.

        All of them as IfcLabel. The declaration names the field but not its
        type — the type is encoded in which of MS Project's fixed slots it
        occupies, Text1 or Number1 or Date1 — and these are short tags either
        way, so reading them as anything else buys nothing and can only fail.

        The generator files these under the key it calls UDFs, which is P6's
        word for its own version of the idea. MS Project has no user-defined
        fields: it has thirty text slots, twenty number slots and so on, which
        a planner may rename. Only the shared slot is borrowed — the property
        set they land in is named for what they are in the file they came from.
        """
        values = {}
        for attribute in task.findall("pr:ExtendedAttribute", self.ns):
            name = self.extended_attributes.get(self.text(attribute, "FieldID"))
            value = self.text(attribute, "Value")
            if name and value:
                values[name] = ("IfcLabel", value)
        return values

    def parse_calendar_xml(self, project):
        calendars = project.find("pr:Calendars", self.ns)
        for calendar in calendars.findall("pr:Calendar", self.ns) if calendars is not None else []:
            calendar_id = self.text(calendar, "UID")
            self.calendars[calendar_id] = {
                "Name": self.text(calendar, "Name"),
                "Type": "Base" if self.text(calendar, "IsBaseCalendar") == "1" else "Derived",
                "HoursPerDay": self.hours_per_day,
                "BaseCalendarUID": self.text(calendar, "BaseCalendarUID"),
                "StandardWorkWeek": self.parse_working_week(calendar),
                "HolidayOrExceptions": self.parse_exceptions(calendar),
            }
        self.inherit_base_calendars()

    def parse_working_week(self, calendar):
        week = []
        week_days = calendar.find("pr:WeekDays", self.ns)
        for week_day in week_days.findall("pr:WeekDay", self.ns) if week_days is not None else []:
            day_of_week = DAY_TYPES.get(self.text(week_day, "DayType"))
            # DayType 0 is not a day of the week at all, it is a date range
            # exception filed in the same list. It is read with the exceptions.
            if day_of_week is None:
                continue
            week.append(
                {
                    "DayOfWeek": day_of_week,
                    "WorkTimes": self.parse_working_times(week_day),
                    "ifc": None,
                }
            )
        return week

    def parse_working_times(self, element):
        times = []
        working_times = element.find("pr:WorkingTimes", self.ns)
        for working_time in working_times.findall("pr:WorkingTime", self.ns) if working_times is not None else []:
            start = self.text(working_time, "FromTime")
            finish = self.text(working_time, "ToTime")
            if not start or not finish:
                continue
            times.append(
                {
                    "Start": datetime.time.fromisoformat(start),
                    "Finish": datetime.time.fromisoformat(finish),
                }
            )
        return times

    def parse_exceptions(self, calendar):
        """Named days that do not follow the working week, keyed year > month.

        MS Project states these twice in the same file: once as an <Exception>,
        and once as a <WeekDay> of DayType 0 carrying the same period, which is
        how the format did it before <Exceptions> existed. Reading both would
        write every holiday into the calendar twice, so the older spelling is
        read only where the newer one is absent.
        """
        exceptions = {}
        exceptions_element = calendar.find("pr:Exceptions", self.ns)
        elements = exceptions_element.findall("pr:Exception", self.ns) if exceptions_element is not None else []
        if not elements:
            week_days = calendar.find("pr:WeekDays", self.ns)
            elements = [
                week_day
                for week_day in (week_days.findall("pr:WeekDay", self.ns) if week_days is not None else [])
                if self.text(week_day, "DayType") == "0"
            ]

        for element in elements:
            for day in self.exception_dates(element):
                month = exceptions.setdefault(day.year, {}).setdefault(day.month, {})
                month.setdefault("FullDay", [])
                month.setdefault("WorkTime", [])
                work_times = self.parse_working_times(element)
                if work_times:
                    month["WorkTime"].append({"Day": day.day, "WorkTimes": work_times, "ifc": None})
                else:
                    month["FullDay"].append(day.day)
        return exceptions

    def exception_dates(self, element):
        """The dates one exception actually covers.

        A one-off exception states the period it applies to and is simply that
        run of days. A recurring one states the period it recurs *within* — a
        public holiday declared yearly spans a decade — and picking the days
        out of that needs MS Project's recurrence rules, which its own
        documentation does not give. The two are told apart by Occurrences: a
        recurrence has fewer of them than the span has days.

        A recurring exception is skipped rather than guessed at. Guessing wrong
        marks working days as holidays, and a calendar that is wrong in that
        direction quietly moves every date computed from it.
        """
        period = element.find("pr:TimePeriod", self.ns)
        start = self.parse_date(period, "FromDate")
        finish = self.parse_date(period, "ToDate")
        if start is None:
            return []
        if finish is None or finish < start:
            finish = start
        days = (finish.date() - start.date()).days + 1

        occurrences = self.text(element, "Occurrences")
        if occurrences and int(occurrences) < days:
            print(
                f"note: skipping recurring calendar exception "
                f"{self.text(element, 'Name') or start.date()} — {occurrences} occurrences "
                f"over {days} days, and the recurrence is not readable from the export"
            )
            return []
        return [start.date() + datetime.timedelta(days=offset) for offset in range(days)]

    def inherit_base_calendars(self):
        """A calendar with no week of its own works its base calendar's week.

        MS Project derives resource and task calendars from a base and stores
        only the differences. An IfcWorkCalendar has no such notion, so what
        was inherited is written out in full.
        """
        for calendar in self.calendars.values():
            seen = set()
            base = calendar
            while not base["StandardWorkWeek"] and base["BaseCalendarUID"] not in seen:
                seen.add(base["BaseCalendarUID"])
                base = self.calendars.get(base["BaseCalendarUID"])
                if base is None:
                    break
                calendar["StandardWorkWeek"] = [dict(day, ifc=None) for day in base["StandardWorkWeek"]]
                if not calendar["HolidayOrExceptions"]:
                    calendar["HolidayOrExceptions"] = base["HolidayOrExceptions"]

    def parse_task_xml(self, project):
        tasks = project.find("pr:Tasks", self.ns)
        elements = [
            task
            for task in (tasks.findall("pr:Task", self.ns) if tasks is not None else [])
            # A null task is a blank row a planner left in the grid. It has no
            # name, no dates and no meaning outside MS Project's own display.
            if self.text(task, "IsNull") != "1"
        ]

        # MS Project's tree is the OutlineLevel column and nothing else: a task
        # belongs to the nearest row above it at a shallower level. Levels are
        # normally 1-based, with 0 used only where the project summary task is
        # exported, so the root is whatever level the file happens to start at
        # rather than a number that can be assumed.
        ancestors = []
        parents = {}
        for task in elements:
            uid = self.text(task, "UID")
            level = int(self.text(task, "OutlineLevel") or 0)
            while ancestors and ancestors[-1][1] >= level:
                ancestors.pop()
            parent = ancestors[-1][0] if ancestors else None
            parents[uid] = parent
            self.children.setdefault(parent, []).append(uid)
            ancestors.append((uid, level))
        self.roots = self.children.pop(None, [])

        for task in elements:
            uid = self.text(task, "UID")
            if self.children.get(uid):
                self.add_wbs(task, uid, parents[uid])
            else:
                self.add_activity(task, uid, parents[uid])

        self.parse_relationship_xml(elements)

    def add_wbs(self, task, uid, parent):
        """A summary task: a branch of the outline, with no work of its own.

        Its dates are MS Project's roll-up of its children rather than anything
        a planner entered, so no IfcTaskTime is written. A reader that wants
        the span of a branch takes it from the leaves, which is where the
        planning actually happened.
        """
        self.wbs[uid] = {
            "Name": self.text(task, "Name") or "",
            "Code": self.text(task, "OutlineNumber") or uid,
            "ParentObjectId": parent,
            "SequenceNumber": 0,
            "UDFs": self.parse_extended_attributes(task),
            "ifc": None,
            "rel": None,
            # Only the leaves directly under this node. The generator's own
            # create_tasks reads this; MSPIfcGenerator walks self.children
            # instead, so that summaries keep their place among them.
            "activities": [child for child in self.children.get(uid, []) if not self.children.get(child)],
        }

    def add_activity(self, task, uid, parent):
        start = self.parse_date(task, "Start")
        finish = self.parse_date(task, "Finish")
        percent_complete = self.text(task, "PercentComplete")
        actual_start = self.parse_date(task, "ActualStart")
        actual_finish = self.parse_date(task, "ActualFinish")

        calendar_id = self.text(task, "CalendarUID")
        # -1 is MS Project for "no calendar of its own".
        if calendar_id in (None, "", "-1") or calendar_id not in self.calendars:
            calendar_id = self.default_calendar_id()

        if parent is None:
            self.root_activities.append(uid)

        self.activities[uid] = {
            "Name": self.text(task, "Name") or "",
            "Identification": self.text(task, "OutlineNumber") or uid,
            "StartDate": start,
            "FinishDate": finish,
            "PlannedDuration": self.parse_duration_hours(task, "Duration"),
            "Status": self.status(percent_complete, actual_start, actual_finish),
            "CalendarObjectId": calendar_id,
            "IsMilestone": self.text(task, "Milestone") == "1" or start == finish,
            "UDFs": self.parse_extended_attributes(task),
            "Codes": {},
            "ActualStartDate": actual_start,
            "ActualFinishDate": actual_finish,
            "EarlyStartDate": self.parse_date(task, "EarlyStart"),
            "EarlyFinishDate": self.parse_date(task, "EarlyFinish"),
            "LateStartDate": self.parse_date(task, "LateStart"),
            "LateFinishDate": self.parse_date(task, "LateFinish"),
            "TotalFloat": self.parse_hours(task, "TotalSlack"),
            "FreeFloat": self.parse_hours(task, "FreeSlack"),
            # IfcTaskTime.Completion is a ratio; MS Project states a percentage.
            "PercentComplete": float(percent_complete) / 100 if percent_complete else None,
            "ifc": None,
        }

        if self.optionalColumns:
            if self.optionalColumns[0] == "all":
                self.optionalColumns = [child.tag.partition("}")[2] for child in task]
            self.activities[uid]["OptionalColumns"] = {
                column: self.text(task, column) for column in self.optionalColumns if self.text(task, column)
            }

    def status(self, percent_complete, actual_start, actual_finish):
        """P6's three words for how far along a task is.

        MS Project has no status column — it has a percentage and, when the
        export carries them, the actual dates. The same three words come out
        either way, so a reader does not have to know which tool the schedule
        was planned in.
        """
        percent = float(percent_complete) if percent_complete else 0
        if actual_finish is not None or percent >= 100:
            return "Completed"
        if actual_start is not None or percent > 0:
            return "In Progress"
        return "Not Started"

    def default_calendar_id(self):
        if self.project["CalendarUID"] in self.calendars:
            return self.project["CalendarUID"]
        return next(iter(self.calendars), None)

    def parse_relationship_xml(self, elements):
        for task in elements:
            successor = self.text(task, "UID")
            for index, link in enumerate(task.findall("pr:PredecessorLink", self.ns)):
                predecessor = self.text(link, "PredecessorUID")
                if predecessor is None:
                    continue
                self.relationships[f"{successor}-{index}"] = {
                    "PredecessorActivity": predecessor,
                    "SuccessorActivity": successor,
                    "Type": SEQUENCE_TYPES.get(self.text(link, "Type"), "FINISH_START"),
                    "Lag": self.parse_lag(link),
                }

    def parse_lag(self, link):
        if self.text(link, "LagFormat") in PERCENT_LAG_FORMATS:
            return 0
        return self.parse_hours(link, "LinkLag") or 0

    def parse_resources_xml(self, project):
        resources = project.find("pr:Resources", self.ns)
        for resource in resources.findall("pr:Resource", self.ns) if resources is not None else []:
            name = self.text(resource, "Name")
            if not name:
                continue
            self.resources[self.text(resource, "UID")] = {
                "Name": name,
                "Code": self.text(resource, "ID"),
                "ParentObjectId": None,
                "Type": self.RESOURCE_TYPES_MAPPING.get(self.text(resource, "Type")),
                "ifc": None,
                "rel": None,
            }
