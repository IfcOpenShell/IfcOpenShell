# Ifc4D - IFC scheduling utility
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import uuid
import datetime
import ifcopenshell
import ifcopenshell.util.date
import ifcopenshell.util.sequence
import xml.etree.ElementTree as ET


class Ifc2Msp:
    def __init__(self):
        self.xml = None
        self.file = None
        self.id = 0
        self.id_map = {}
        self.element_map = {}
        self.hours_per_day = 8
        self.project_tasks = []
        self.start_dates = []
        self.base_calendar = None
        # P6XML does not understand patterns in holiday dates. Instead, it
        # expects a list of every day that is a holiday between a date range.
        # This allows you to specify the date range where the export should
        # calculate holidays for.
        self.holiday_start_date = None
        self.holiday_finish_date = None
        self.work_schedule = None

    def execute(self):
        self.root = ET.Element("Project")
        self.root.attrib["xmlns"] = "http://schemas.microsoft.com/project"

        self.schedule = self.file.by_type("IfcWorkSchedule")[0]

        self.create_project()
        self.create_calendars()
        self.create_tasks()

        self.set_start_date()
        self.set_base_calendar()

        tree = ET.ElementTree(self.root)
        tree.write(self.xml, encoding="utf-8", xml_declaration=True)

    def create_project(self):
        # Which version should we pick? I don't know. Hardcode as 14 until it breaks :)
        # Values are: 12=Project 2007, 24=Project 2010
        ET.SubElement(self.root, "SaveVersion").text = "14"
        element = self.file.by_type("IfcProject")[0]
        self.link_element(element, self.root)
        ET.SubElement(self.root, "GUID").text = str(uuid.UUID(ifcopenshell.guid.expand(element.GlobalId))).upper()
        ET.SubElement(self.root, "Name").text = element.Name or "X"
        ET.SubElement(self.root, "Title").text = element.LongName or "Unnamed"
        # This is mandatory, but we don't use it
        ET.SubElement(self.root, "CurrencyCode").text = "USD"
        ET.SubElement(self.root, "DurationFormat").text = "7"
        ET.SubElement(self.root, "MinutesPerDay").text = "480"

    def set_start_date(self):
        ET.SubElement(self.root, "ScheduleFromStart").text = "1"
        if self.start_dates:
            # Set to midnight as a workaround. If I don't, the first duration seems to stick to zero.
            ET.SubElement(self.root, "StartDate").text = sorted(self.start_dates)[0].split("T")[0] + "T00:00:00"

    def set_base_calendar(self):
        if self.base_calendar:
            ET.SubElement(self.root, "CalendarUID").text = self.id_map[self.base_calendar]

    def create_calendars(self):
        el = ET.SubElement(self.root, "Calendars")
        for calendar in self.file.by_type("IfcWorkCalendar"):
            self.create_calendar(calendar, el)

    def create_calendar(self, calendar, parent):
        el = ET.SubElement(parent, "Calendar")
        self.link_element(calendar, el)
        ET.SubElement(el, "Name").text = calendar.Name or "Unnamed"
        ET.SubElement(el, "IsBaseCalendar").text = "1"

        working_week = self.auto_detect_working_week(calendar)

        if not working_week:
            working_week = self.get_default_working_week()

        week_days = ET.SubElement(el, "WeekDays")

        day_map = {
            "Sunday": "1",
            "Monday": "2",
            "Tuesday": "3",
            "Wednesday": "4",
            "Thursday": "5",
            "Friday": "6",
            "Saturday": "7",
        }

        for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
            time_periods = working_week.get(day, None)
            if time_periods:
                week_day = ET.SubElement(week_days, "WeekDay")
                ET.SubElement(week_day, "DayType").text = day_map[day]
                ET.SubElement(week_day, "DayWorking").text = "1"
                working_times = ET.SubElement(week_day, "WorkingTimes")
                for time_period in time_periods:
                    working_time = ET.SubElement(working_times, "WorkingTime")
                    ET.SubElement(working_time, "FromTime").text = time_period["Start"]
                    ET.SubElement(working_time, "ToTime").text = time_period["Finish"]
            else:
                week_day = ET.SubElement(week_days, "WeekDay")
                ET.SubElement(week_day, "DayType").text = day_map[day]
                ET.SubElement(week_day, "DayWorking").text = "0"

        # TODO Exceptions not yet implemented
        return

        holidays = ET.SubElement(el, "Exceptions")
        for holiday in self.auto_detect_holidays(calendar):
            el = ET.SubElement(holidays, "Exception")
            # Recurrence is supported but I haven't implemented it yet
            holiday = ifcopenshell.util.date.datetime2ifc(holiday, "IfcDateTime")
            time_period = ET.SubElement(el, "TimePeriod")
            ET.SubElement(time_period, "FromDate").text = holiday
            ET.SubElement(time_period, "ToDate").text = holiday

    def auto_detect_working_week(self, calendar):
        # Microsoft Project XML only understands a working week. In other words,
        # it understands the equivalent of an IFC weekly recurring time period.
        # If you do not have a weekly recurring time period, we just give a
        # default working week.
        results = {}
        weekday_component_map = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday",
        }
        for working_time in calendar.WorkingTimes:
            if not working_time.RecurrencePattern or working_time.RecurrencePattern.RecurrenceType != "WEEKLY":
                continue

            if not working_time.RecurrencePattern.TimePeriods:
                time_periods = [{"Start": "09:00:00", "Finish": "17:00:00"}]
            else:
                time_periods = [
                    {"Start": p.StartTime, "Finish": p.EndTime} for p in working_time.RecurrencePattern.TimePeriods
                ]

            for component in working_time.RecurrencePattern.WeekdayComponent:
                results.setdefault(weekday_component_map[component], []).extend(time_periods)

        return results

    def get_default_working_week(self):
        results = {}
        # As a fallback, we work 5 days a week, 8 hours per day.
        for name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            results[name] = [{"Start": "09:00:00", "Finish": "17:00:00"}]
        return results

    def auto_detect_holidays(self, calendar):
        results = []
        start = self.holiday_start_date
        finish = self.holiday_finish_date
        if finish < start:
            return results
        while start < finish:
            start += datetime.timedelta(days=1)
            if not ifcopenshell.util.sequence.is_working_day(start, calendar):
                results.append(start)
        return results

    def create_tasks(self):
        self.tasks = ET.SubElement(self.root, "Tasks")
        for task in self.get_subtasks(self.work_schedule):
            self.create_task(task)

    def create_task(self, task, level=0):
        el = ET.SubElement(self.tasks, "Task")
        self.link_element(task, el)
        ET.SubElement(el, "Name").text = task.Name or "Unnamed"
        ET.SubElement(el, "OutlineNumber").text = task.Identification or "X"
        ET.SubElement(el, "OutlineLevel").text = str(level)
        ET.SubElement(el, "DurationFormat").text = "53"
        if task.TaskTime:
            if task.TaskTime.ScheduleDuration:
                duration = ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration)
                ET.SubElement(el, "Duration").text = f"PT{duration.days * 8}H0M0S"
            if task.TaskTime.ScheduleStart:
                ET.SubElement(el, "Start").text = task.TaskTime.ScheduleStart
                self.start_dates.append(task.TaskTime.ScheduleStart)
            if task.TaskTime.ScheduleFinish:
                ET.SubElement(el, "Finish").text = task.TaskTime.ScheduleFinish
            ET.SubElement(el, "Critical").text = "1" if task.TaskTime.IsCritical else "0"

            data_map = {
                "EarlyStart": task.TaskTime.EarlyStart,
                "EarlyFinish": task.TaskTime.EarlyFinish,
                "LateStart": task.TaskTime.LateStart,
                "LateFinish": task.TaskTime.LateFinish,
            }
            for key, value in data_map.items():
                if value:
                    ET.SubElement(el, key).text = value

        calendar = ifcopenshell.util.sequence.derive_calendar(task)
        if calendar:
            ET.SubElement(el, "CalendarUID").text = self.id_map[calendar]
            if level == 0:
                # This must be the base calendar
                self.base_calendar = calendar

        for rel in task.IsSuccessorFrom or []:
            predecessor = rel.RelatingProcess
            predecessor_link = ET.SubElement(el, "PredecessorLink")
            self.link_element(rel, predecessor_link)
            if rel.TimeLag and rel.TimeLag.LagValue:
                duration = ifcopenshell.util.date.ifc2datetime(rel.TimeLag.LagValue.wrappedValue)
                # Lag time is expressed in tenths of a minute. Seriously, Microsoft?
                ET.SubElement(predecessor_link, "LinkLag").text = str(duration.days * self.hours_per_day * 60 * 10)
            else:
                ET.SubElement(predecessor_link, "LinkLag").text = "0"
            ET.SubElement(predecessor_link, "PredecessorUID").text = str(predecessor.id())
            ET.SubElement(predecessor_link, "Type").text = {
                "START_START": "3",
                "START_FINISH": "2",
                "FINISH_START": "1",
                "FINISH_FINISH": "0",
                "NOTDEFINED": "1",
                "USERDEFINED": "1",
                None: "1",
            }[rel.SequenceType]

        for subtask in self.get_subtasks(task):
            self.create_task(subtask, level=level + 1)

    def get_subtasks(self, element):
        tasks = []
        if element.is_a("IfcWorkSchedule"):
            for rel in element.Controls or []:
                tasks.extend([e for e in rel.RelatedObjects if e.is_a("IfcTask")])
        elif element.is_a("IfcTask"):
            for rel in element.IsNestedBy or []:
                tasks.extend([e for e in rel.RelatedObjects if e.is_a("IfcTask")])
        return tasks

    def link_element(self, element, el):
        ET.SubElement(el, "UID").text = str(element.id())
        ET.SubElement(el, "GUID").text = str(uuid.UUID(ifcopenshell.guid.expand(element.GlobalId))).upper()
        self.id_map[element] = str(element.id())
        self.element_map[element] = el
