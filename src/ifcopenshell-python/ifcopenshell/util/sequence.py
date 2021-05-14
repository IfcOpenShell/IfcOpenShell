import datetime
import ifcopenshell.util.date


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
        if is_working_day(current_date, calendar):
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


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
    print('is day working day ', day, is_working_day)
    return is_working_day


def is_work_time_applicable_to_day(work_time, day):
    start = None
    finish = None

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
