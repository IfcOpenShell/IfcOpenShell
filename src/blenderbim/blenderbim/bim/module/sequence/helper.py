import math
import isodate
import datetime
from dateutil import parser
from ifcopenshell.api.sequence.data import Data


def count_working_days(start, finish, calendar):
    result = 0
    current_date = datetime.date(start.year, start.month, start.day)
    finish_date = datetime.date(finish.year, finish.month, finish.day)
    while current_date <= finish_date:
        if is_working_day(current_date, calendar):
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def is_working_day(day, calendar):
    is_working_day = False
    for work_time_id in calendar["WorkingTimes"] or []:
        if is_work_time_applicable_to_day(Data.work_times[work_time_id], day):
            is_working_day = True
            break
    if not is_working_day:
        return is_working_day
    for work_time_id in calendar["ExceptionTimes"] or []:
        if is_work_time_applicable_to_day(Data.work_times[work_time_id], day):
            is_working_day = False
            break
    return is_working_day


def is_work_time_applicable_to_day(work_time, day):
    if work_time["Start"] and work_time["Start"] > day:
        return False

    if work_time["Finish"] and work_time["Finish"] < day:
        return False

    if not work_time["RecurrencePattern"]:
        return True

    recurrence = Data.recurrence_patterns[work_time["RecurrencePattern"]]

    if recurrence["RecurrenceType"] == "DAILY":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return True
        if not work_time["Start"]:
            return False
        return False  # TODO
    elif recurrence["RecurrenceType"] == "WEEKLY":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return (day.weekday() + 1) in recurrence["WeekdayComponent"]
        if not work_time["Start"]:
            return False
        return False  # TODO
    elif recurrence["RecurrenceType"] == "MONTHLY_BY_DAY_OF_MONTH":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return day.day in recurrence["DayComponent"]
        return False  # TODO
    elif recurrence["RecurrenceType"] == "MONTHLY_BY_POSITION":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return (day.weekday() + 1) in recurrence["WeekdayComponent"] and math.floor(day.day / 7) + 1 == recurrence[
                "Position"
            ]
        return False  # TODO
    elif recurrence["RecurrenceType"] == "YEARLY_BY_DAY_OF_MONTH":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return day.month in recurrence["MonthComponent"] and day.day in recurrence["DayComponent"]
        return False  # TODO
    elif recurrence["RecurrenceType"] == "YEARLY_BY_POSITION":
        if not recurrence["Interval"] and not recurrence["Occurrences"]:
            return (
                day.month in recurrence["MonthComponent"]
                and (day.weekday() + 1) in recurrence["WeekdayComponent"]
                and math.floor(day.day / 7) + 1 == recurrence["Position"]
            )
        return False  # TODO


def derive_date(ifc_definition_id, attribute_name, date=None, is_earliest=False, is_latest=False):
    task = Data.tasks[ifc_definition_id]
    if task["TaskTime"]:
        current_date = Data.task_times[task["TaskTime"]][attribute_name]
        if current_date:
            return current_date
    for subtask in task["RelatedObjects"]:
        current_date = derive_date(
            subtask, attribute_name, date=date, is_earliest=is_earliest, is_latest=is_latest
        )
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def parse_datetime(value):
    try:
        return parser.isoparse(value)
    except:
        try:
            return parser.parse(value, dayfirst=True, fuzzy=True)
        except:
            return None


def parse_duration(value):
    try:
        return isodate.parse_duration(value)
    except:
        return None
