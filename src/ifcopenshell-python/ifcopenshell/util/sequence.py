# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import ifcopenshell.util.date
from functools import lru_cache


def derive_calendar(task):
    calendar = [
        rel.RelatingControl
        for rel in task.HasAssignments or []
        if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkCalendar")
    ]
    if calendar:
        return calendar[0]
    for rel in task.Nests or []:
        return derive_calendar(rel.RelatingObject)


def count_working_days(start, finish, calendar):
    result = 0
    current_date = datetime.date(start.year, start.month, start.day)
    finish_date = datetime.date(finish.year, finish.month, finish.day)
    while current_date < finish_date:
        if calendar and calendar.WorkingTimes and is_working_day(current_date, calendar):
            result += 1
        elif not calendar:
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def get_start_or_finish_date(start, duration, duration_type, calendar, date_type="FINISH"):
    if not duration.days:
        # Typically a milestone will have zero duration, so the start == finish
        return start
    # We minus 1 because the start day itself is counted as a day
    duration = datetime.timedelta(days=duration.days - 1)
    if date_type == "START":
        duration = -duration
    result = offset_date(start, duration, duration_type, calendar)
    if date_type == "START":
        return datetime.datetime.combine(result, datetime.time(9))
    return datetime.datetime.combine(result, datetime.time(17))


def offset_date(start, duration, duration_type, calendar):
    current_date = start
    abs_duration = abs(duration.days)
    date_offset = datetime.timedelta(days=1 if duration.days > 0 else -1)
    while abs_duration > 0:
        if duration_type == "ELAPSEDTIME" or not calendar or not calendar.WorkingTimes:
            abs_duration -= 1
        elif ifcopenshell.util.sequence.is_working_day(current_date, calendar):
            abs_duration -= 1
        current_date += date_offset

    if duration.days > 0:
        current_date = get_soonest_working_day(current_date, duration_type, calendar)
    else:
        current_date = get_recent_working_day(current_date, duration_type, calendar)
    return current_date


def get_soonest_working_day(start, duration_type, calendar):
    if duration_type == "ELAPSEDTIME" or not calendar or not calendar.WorkingTimes:
        return start
    while not is_working_day(start, calendar):
        start += datetime.timedelta(days=1)
    return start


def get_recent_working_day(start, duration_type, calendar):
    if duration_type == "ELAPSEDTIME" or not calendar or not calendar.WorkingTimes:
        return start
    while not is_working_day(start, calendar):
        start -= datetime.timedelta(days=1)
    return start


@lru_cache(maxsize=None)
def is_working_day(day, calendar):
    is_working_day = False
    for work_time in calendar.WorkingTimes or []:
        if is_work_time_applicable_to_day(work_time, day):
            is_working_day = True
            break
    if not is_working_day:
        return is_working_day
    for work_time in calendar.ExceptionTimes or []:
        if is_work_time_applicable_to_day(work_time, day):
            is_working_day = False
            break
    return is_working_day


def is_work_time_applicable_to_day(work_time, day):
    start = None
    finish = None
    if isinstance(day, datetime.datetime):
        day = datetime.date(day.year, day.month, day.day)

    if work_time.Start:
        start = ifcopenshell.util.date.ifc2datetime(work_time.Start)
        if start > day:
            return False

    if work_time.Finish:
        finish = ifcopenshell.util.date.ifc2datetime(work_time.Finish)
        if finish < day:
            return False

    if not work_time.RecurrencePattern:
        return True

    recurrence = work_time.RecurrencePattern

    if recurrence.RecurrenceType == "DAILY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return True
        if not work_time.Start:
            return False
        return False  # TODO
    elif recurrence.RecurrenceType == "WEEKLY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent
        if not work_time.Start:
            return False
        return False  # TODO
    elif recurrence.RecurrenceType == "MONTHLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence.RecurrenceType == "MONTHLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent and math.floor(day.day / 7) + 1 == recurrence[
                "Position"
            ]
        return False  # TODO
    elif recurrence.RecurrenceType == "YEARLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.month in recurrence.MonthComponent and day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence.RecurrenceType == "YEARLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (
                day.month in recurrence.MonthComponent
                and (day.weekday() + 1) in recurrence.WeekdayComponent
                and math.floor(day.day / 7) + 1 == recurrence.Position
            )
        return False  # TODO
