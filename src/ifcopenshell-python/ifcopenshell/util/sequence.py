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
from collections.abc import Generator
from fractions import Fraction
from functools import cache
from math import floor
from typing import Literal, Optional, Union

from dateutil.relativedelta import relativedelta

import ifcopenshell.util.date
import ifcopenshell.util.element

DURATION_TYPE = Literal["ELAPSEDTIME", "WORKTIME", "NOTDEFINED"]
ZERO = datetime.timedelta()
MICROSECOND = datetime.timedelta(microseconds=1)
RECURRENCE_TYPE = Literal[
    "BY_DAY_COUNT",
    "BY_WEEKDAY_COUNT",
    "DAILY",
    "MONTHLY_BY_DAY_OF_MONTH",
    "MONTHLY_BY_POSITION",
    "WEEKLY",
    "YEARLY_BY_DAY_OF_MONTH",
    "YEARLY_BY_POSITION",
]


def derive_date(
    task: ifcopenshell.entity_instance,
    attribute_name: str,
    date=None,
    is_earliest: bool = False,
    is_latest: bool = False,
):
    """

    :param task: IfcTask.

    """
    if task.TaskTime:
        current_date = (
            ifcopenshell.util.date.ifc2datetime(getattr(task.TaskTime, attribute_name))
            if getattr(task.TaskTime, attribute_name)
            else ""
        )
        if current_date:
            return current_date
    for subtask in get_all_nested_tasks(task):
        current_date = derive_date(
            subtask,
            attribute_name,
            date=date,
            is_earliest=is_earliest,
            is_latest=is_latest,
        )
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def derive_calendar(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    calendar = get_calendar(task)
    if calendar:
        return calendar
    for rel in task.Nests or []:
        return derive_calendar(rel.RelatingObject)


def get_calendar(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    calendar = [
        rel.RelatingControl
        for rel in task.HasAssignments or []
        if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkCalendar")
    ]
    if calendar:
        return calendar[0]


def count_working_days(start, finish, calendar: ifcopenshell.entity_instance) -> int:
    result = 0
    if start == finish:
        return 0
    current_date = datetime.date(start.year, start.month, start.day)
    finish_date = datetime.date(finish.year, finish.month, finish.day)
    while current_date <= finish_date:
        if calendar and calendar.WorkingTimes and is_working_day(current_date, calendar):
            result += 1
        elif not calendar or not is_calendar_applicable(current_date, calendar):
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def get_start_or_finish_date(
    start,
    duration,
    duration_type: DURATION_TYPE,
    calendar: ifcopenshell.entity_instance,
    date_type: Literal["START", "FINISH"] = "FINISH",
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
):
    """Get the finish of a task from its start, or its start from its finish

    A WORKTIME duration of work days counts whole working days, each with
    the length of its own work periods. A part of a day has no length that
    all the days share, thus it counts as a full day (it rounds up): a task
    of work days starts at the start of a working day. P1D from Thursday
    13:00 takes all of Friday. Work hours are exact: PT8H from Thursday
    13:00 finishes on Friday at 13:00, and P1DT4H from the start of a day
    finishes 4 work hours after the end of that day. An ELAPSEDTIME duration
    is continuous time.

    :param start: The start (for FINISH) or the finish (for START).
    :param duration: The duration, an IfcDuration, or a timedelta whose
        days are work days.
    :param duration_type: The IfcTaskDurationEnum of the duration.
    :param calendar: The IfcWorkCalendar, or None.
    :param date_type: FINISH to get the finish from the start, START to get
        the latest start that finishes at or before the finish.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :return: The finish or the start.
    """
    if not any(_get_duration_parts(duration)):
        # Typically a milestone will have zero duration, so the start == finish
        return start
    if date_type == "FINISH":
        # A task of work days starts at the start of a working day: a part of a day counts as a full day.
        start = snap_task_date(start, "START", duration, duration_type, calendar, work_day)
    result = offset_date(
        start, negate_duration(duration) if date_type == "START" else duration, duration_type, calendar, work_day
    )
    if duration_type == "ELAPSEDTIME":
        return result  # Elapsed time does not stop out of the work periods
    if date_type == "START":
        # The latest start of a task of work days that finishes at or before the finish
        result = snap_task_date(result, "START", duration, duration_type, calendar, work_day, is_forward=False)
        return get_work_start(result, calendar, work_day)
    return get_work_finish(result, calendar, work_day)


def _get_duration_parts(duration) -> tuple[float, datetime.timedelta, float, float]:
    """Get the work days, the work time, the months and the years of a duration

    The date part and the time part of an IfcDuration stay apart: P1D is one
    work day and PT24H is 24 work hours. For a timedelta, the days are work
    days and the rest is work time. Each part has the sign of the duration.
    """
    if not duration:
        return 0, ZERO, 0, 0
    if isinstance(duration, str):
        sign = -1 if duration.startswith("-") else 1
        date_part, _, time_part = duration.lstrip("-").partition("T")
        date = ifcopenshell.util.date.parse_duration(date_part) if date_part != "P" else ZERO
        time = ifcopenshell.util.date.parse_duration("PT" + time_part) if time_part else ZERO
        days = getattr(date, "tdelta", date) / datetime.timedelta(days=1)
        months, years = getattr(date, "months", 0), getattr(date, "years", 0)
        return sign * days, sign * getattr(time, "tdelta", time), sign * months, sign * years
    months, years = getattr(duration, "months", 0), getattr(duration, "years", 0)
    delta = getattr(duration, "tdelta", duration) or ZERO
    sign = -1 if delta < ZERO else 1
    days = abs(delta).days
    return sign * days, sign * (abs(delta) - datetime.timedelta(days=days)), months, years


def negate_duration(duration):
    """Negate an IfcDuration or a timedelta"""
    if isinstance(duration, str):
        return duration[1:] if duration.startswith("-") else "-" + duration
    return -duration


def _format_work_duration(days: int, time: datetime.timedelta) -> str:
    """Write work days and work time as an IfcDuration. The work time stays in hours: PT30H, not P1DT6H."""
    sign = "-" if days < 0 or time < ZERO else ""
    days, time = abs(days), abs(time)
    hours, rest = divmod(time, datetime.timedelta(hours=1))
    minutes, rest = divmod(rest, datetime.timedelta(minutes=1))
    parts = "".join(f"{value}{unit}" for value, unit in ((hours, "H"), (minutes, "M")) if value)
    if rest:
        parts += f"{rest.total_seconds():.6f}".rstrip("0").rstrip(".") + "S"
    result = (f"{days}D" if days else "") + (f"T{parts}" if parts else "")
    return f"{sign}P{result}" if result else "P0D"


def offset_date(
    start,
    duration,
    duration_type: DURATION_TYPE,
    calendar: ifcopenshell.entity_instance,
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
):
    """Offset a datetime by a duration

    An ELAPSEDTIME duration is continuous time. A WORKTIME duration moves the
    work days first (see offset_work_days), then the work time (see
    offset_work_time). A negative WORKTIME duration does the same steps in
    the reverse order. Thus, from the start of a working day, a negative
    duration reverses a positive duration.

    :param start: The datetime to offset.
    :param duration: An IfcDuration, or a timedelta whose days are work days.
    :param duration_type: The IfcTaskDurationEnum of the duration.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :return: The datetime after (or before) the duration.
    """
    days, time, months, years = _get_duration_parts(duration)
    if not isinstance(start, datetime.datetime):  # A date: whole working days
        result = offset_date(
            datetime.datetime.combine(start, datetime.time()), duration, duration_type, calendar, work_day
        )
        return result.date()
    current_date = start
    if months or years:
        # IfcDuration years and months are calendar years and months
        current_date += relativedelta(years=int(years), months=int(months))
    if duration_type == "ELAPSEDTIME":
        return current_date + datetime.timedelta(days=days) + time
    if min(days, time / datetime.timedelta(days=1), months, years) < 0:
        current_date = offset_work_time(current_date, time, calendar, work_day)
        return offset_work_days(current_date, days, calendar, work_day)
    current_date = offset_work_days(current_date, days, calendar, work_day)
    return offset_work_time(current_date, time, calendar, work_day)


def get_work_day(
    date: datetime.datetime,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
) -> tuple[datetime.date, int, int]:
    """Get the working day of a datetime, and the position in that day

    The end of a work day and the start of the next work day are the same
    work instant. Forward, that instant is the start of the next work day.
    Backward, it is the end of the previous work day.

    :return: The working day, the work time before the datetime in that day,
        and the work time of that day. The work times are in microseconds.
    """
    if is_forward:
        date = get_work_start(date, calendar, work_day)
    else:
        date = get_work_finish(date, calendar, work_day)
    day = date.date()
    periods = get_work_periods(day, calendar, work_day)
    midnight = datetime.datetime.combine(day, datetime.time(), date.tzinfo)
    done = sum((min(end, date - midnight) - start for start, end in periods if start < date - midnight), ZERO)
    length = sum((end - start for start, end in periods), ZERO)
    return day, done // MICROSECOND, length // MICROSECOND


def get_day_limits(
    day: datetime.date,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    tzinfo=None,
) -> tuple[datetime.datetime, datetime.datetime]:
    """Get the start of the first work period and the end of the last work period of a working day"""
    periods = get_work_periods(day, calendar, work_day)
    midnight = datetime.datetime.combine(day, datetime.time(), tzinfo)
    return midnight + periods[0][0], midnight + periods[-1][1]


def snap_work_day(
    date: datetime.datetime,
    date_type: Literal["START", "FINISH"],
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
) -> datetime.datetime:
    """Move a date in a working day to the start or the end of a working day

    A duration of work days is exact only from the start of a working day,
    because the working days of a calendar can have different lengths. A
    part of a day thus counts as a full day (it rounds up), and a task of
    work days starts at the start of a working day and finishes at the end
    of a working day.

    Forward, a START in a day moves to the start of the next working day,
    and a FINISH in a day moves to the end of that day. Backward, a START in
    a day moves to the start of that day, and a FINISH in a day moves to the
    end of the previous working day. A date at a limit of a working day, or
    out of the work periods between two days, moves to that limit.

    :param date: The datetime to move.
    :param date_type: START or FINISH.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :param is_forward: True to move to a later limit, False to an earlier one.
    :return: The start or the end of a working day.
    """
    if date_type == "START":
        day, done, length = get_work_day(date, calendar, work_day, is_forward=True)
        if not length:
            return date  # No work time in the calendar
        if done and is_forward:
            day = get_working_day(day, 1, calendar, work_day)
        return get_day_limits(day, calendar, work_day, date.tzinfo)[0]
    day, done, length = get_work_day(date, calendar, work_day, is_forward=False)
    if not length:
        return date
    if done < length and not is_forward:
        day = get_working_day(day, -1, calendar, work_day)
    return get_day_limits(day, calendar, work_day, date.tzinfo)[1]


def snap_task_date(
    date: datetime.datetime,
    date_type: Literal["START", "FINISH"],
    duration,
    duration_type: Optional[DURATION_TYPE],
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
) -> datetime.datetime:
    """Move the start or the finish of a task of work days to a limit of a working day

    A task with a WORKTIME duration of work days starts at the start of a
    working day, because a part of a day counts as a full day (see
    snap_work_day). If the duration is whole work days only, the task also
    finishes at the end of a working day. Work hours after the work days are
    exact, thus the finish of P1DT4H does not move. A task of work hours
    only, a task in ELAPSEDTIME and a milestone do not move.

    :param date: The start or the finish of the task.
    :param date_type: START or FINISH.
    :param duration: The duration of the task, an IfcDuration, or a timedelta whose
        days are work days.
    :param duration_type: The IfcTaskDurationEnum of the duration.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :param is_forward: True to move to a later limit, False to an earlier one.
    :return: The date, moved if necessary.
    """
    if duration_type == "ELAPSEDTIME" or not isinstance(date, datetime.datetime):
        return date
    days, time = _get_duration_parts(duration)[:2]
    if not days or (date_type == "FINISH" and time):
        return date
    return snap_work_day(date, date_type, calendar, work_day, is_forward)


def get_task_dates_from_finish(
    finish: datetime.datetime,
    duration,
    duration_type: Optional[DURATION_TYPE],
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
) -> tuple[datetime.datetime, datetime.datetime]:
    """Get the start and the finish of a task from a limit of its finish

    A task of work days starts at the start of a working day (see
    snap_task_date), thus its finish cannot always be at the limit. Forward,
    the limit is the earliest finish: the task finishes at or after it.
    Backward, the limit is the latest finish: the task finishes at or before
    it. Other tasks finish at the limit.

    :param finish: The limit of the finish.
    :param duration: The duration of the task, an IfcDuration, or a timedelta whose
        days are work days.
    :param duration_type: The IfcTaskDurationEnum of the duration.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :param is_forward: True for an earliest finish, False for a latest finish.
    :return: The start and the finish of the task.
    """
    start = get_start_or_finish_date(finish, duration, duration_type, calendar, "START", work_day)
    if duration_type == "ELAPSEDTIME" or not _get_duration_parts(duration)[0]:
        return start, finish
    result = get_start_or_finish_date(start, duration, duration_type, calendar, "FINISH", work_day)
    if is_forward and get_work_time(result, finish, calendar, work_day) > ZERO:
        start = offset_work_days(start, 1, calendar, work_day)  # The start of the next working day
        result = get_start_or_finish_date(start, duration, duration_type, calendar, "FINISH", work_day)
    return start, result


def offset_work_days(
    start: datetime.datetime,
    days: float,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.datetime:
    """Offset an instant by work days

    Each work day is one working day of the calendar, with the length of its
    own work periods. The result is at the same position in its working day
    as the start: 13:00 in a day from 09:00 to 17:00 is half of the day, and
    one work day later is half of the next working day. Thus a later start
    never gives an earlier result, and a negative offset reverses a positive
    offset. This is necessary for a lag, because the late dates of a
    schedule reverse its early dates.

    A task of work days does not use a part of a day: it starts at the start
    of a working day (see snap_task_date and get_start_or_finish_date). From
    the start of a day, the work days are whole working days.

    :param start: The datetime to offset.
    :param days: The work days. Can have decimals, and can be negative.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day if the calendar has no time
        period. See get_work_periods.
    :return: The datetime after (or before) the work days.
    """
    if not days:
        return start
    day, done, length = get_work_day(start, calendar, work_day, is_forward=days > 0)
    if not length:
        return start  # No work time in the calendar
    target = Fraction(done, length) + Fraction(str(days))
    steps = floor(target)
    position = target - steps
    # At a limit between two days, the result is on the same side as the start: from the end of a day, the end of a
    # day; else, the start of a day. Both are the same work instant.
    if not position and snap_work_day(start, "FINISH", calendar, work_day, is_forward=False) == start:
        steps, position = steps - 1, Fraction(1)
    day = get_working_day(day, steps, calendar, work_day)
    periods = get_work_periods(day, calendar, work_day)
    if not periods:
        return start  # No work time in the calendar
    length = sum((end - start for start, end in periods), ZERO) // MICROSECOND
    midnight = datetime.datetime.combine(day, datetime.time(), start.tzinfo)
    work = datetime.timedelta(microseconds=round(position * length))
    result = offset_work_time(midnight + periods[0][0], work, calendar, work_day)
    # At a limit between two work periods (12:00 and 13:00 around a break), the result is on the same side as the
    # start: from the end of a work period, the end of a work period; else, the start of the next work period. Both
    # are the same work instant, but not the same instant for a task in other work periods or in elapsed time.
    if get_work_finish(start, calendar, work_day) == start != get_work_start(start, calendar, work_day):
        return result
    return result if result == midnight + periods[-1][1] else get_work_start(result, calendar, work_day)


def get_working_day(
    day: datetime.date,
    steps: int,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.date:
    """Get the working day a number of working days after (or before) a day"""
    step = datetime.timedelta(days=1 if steps > 0 else -1)
    days_without_work = 0
    while steps and days_without_work < 366:
        day += step
        if get_work_periods(day, calendar, work_day):
            steps -= 1 if steps > 0 else -1
            days_without_work = 0
        else:
            days_without_work += 1
    return day


def get_work_duration_between(
    start: datetime.datetime,
    finish: datetime.datetime,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> str:
    """Get the work days and work time from a start to a finish

    Work days are exact only from the start of a working day (see
    offset_work_days). From the start of a day, the result is the whole
    working days to the finish and the work time after them. From another
    datetime, the result is the work time only.

    :return: An IfcDuration. offset_date with it from the start gives the
        finish. The work time stays in hours (PT30H, not P1DT6H).
    """
    if finish < start:
        return _format_work_duration(0, -get_work_time(finish, start, calendar, work_day))
    if snap_work_day(start, "START", calendar, work_day) != start:
        return _format_work_duration(0, get_work_time(start, finish, calendar, work_day))
    days = 0
    day = start.date()
    day_end = start
    while (end := get_day_limits(day, calendar, work_day, start.tzinfo)[1]) <= finish:
        days, day_end = days + 1, end
        day = get_working_day(day, 1, calendar, work_day)
    return _format_work_duration(days, get_work_time(day_end, finish, calendar, work_day))


def offset_work_time(
    start: datetime.datetime,
    duration: datetime.timedelta,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.datetime:
    """Offset a datetime by a work time, through the work periods of each day

    :param start: The datetime to offset.
    :param duration: The work time. A negative work time offsets back.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day. See get_work_periods.
    :return: The datetime after (or before) the work time. A result at the
        limit of a work period stays at that limit.
    """
    sign = -1 if duration < datetime.timedelta() else 1
    remaining = abs(duration)
    day = start.date()
    days_without_work = 0
    while remaining and days_without_work < 366:
        midnight = datetime.datetime.combine(day, datetime.time(), start.tzinfo)
        periods = get_work_periods(day, calendar, work_day)
        days_without_work = 0 if periods else days_without_work + 1
        for period_start, period_end in periods if sign > 0 else reversed(periods):
            period_start, period_end = midnight + period_start, midnight + period_end
            if sign > 0 and start < period_end:
                start = max(start, period_start)
                step = min(remaining, period_end - start)
            elif sign < 0 and start > period_start:
                start = min(start, period_end)
                step = min(remaining, start - period_start)
            else:
                continue
            start += sign * step
            remaining -= step
            if not remaining:
                break
        day += datetime.timedelta(days=sign)
    return start


def get_work_time(
    start: datetime.datetime,
    finish: datetime.datetime,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.timedelta:
    """Get the work time between two datetimes

    :param start: The first datetime.
    :param finish: The second datetime. If it is before the start, the work
        time is negative.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of a work day. See get_work_periods.
    :return: The sum of the work periods between the two datetimes.
    """
    if finish < start:
        return -get_work_time(finish, start, calendar, work_day)
    work = datetime.timedelta()
    day = start.date()
    while day <= finish.date():
        midnight = datetime.datetime.combine(day, datetime.time(), start.tzinfo)
        for period_start, period_end in get_work_periods(day, calendar, work_day):
            overlap = min(finish, midnight + period_end) - max(start, midnight + period_start)
            work += max(overlap, datetime.timedelta())
        day += datetime.timedelta(days=1)
    return work


def get_work_start(
    date: datetime.datetime,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.datetime:
    """Get the first work instant at or after a datetime

    A datetime in a work period does not change. A datetime at the end of a
    work period, or out of the work periods, moves to the start of the next
    work period.
    """
    instant = datetime.timedelta(microseconds=1)
    return offset_work_time(date, instant, calendar, work_day) - instant


def get_work_finish(
    date: datetime.datetime,
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
) -> datetime.datetime:
    """Get the last work instant at or before a datetime

    A datetime in a work period does not change. A datetime at the start of
    a work period, or out of the work periods, moves to the end of the
    previous work period.
    """
    instant = datetime.timedelta(microseconds=1)
    return offset_work_time(date, -instant, calendar, work_day) + instant


def offset_lag(
    date: datetime.datetime,
    lag: datetime.timedelta,
    lag_type: Optional[DURATION_TYPE],
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
) -> datetime.datetime:
    """Offset a date of a predecessor by the lag of a sequence

    :param date: The date of the predecessor (forward), or of the successor
        (backward).
    :param lag: The lag, from get_lag_time.
    :param lag_type: The IfcLagTime DurationType. ELAPSEDTIME is continuous
        time. Other values are work time of the calendar.
    :param calendar: The IfcWorkCalendar of the successor, or None.
    :param work_day: The length of a work day of the successor.
    :param is_forward: True to add the lag, False to subtract it.
    :return: The offset date. For a lag in work time, the end of a pause in
        the work (for example 17:00 and 09:00 the next day) gives the
        earliest date (forward) or the latest date (backward).
    """
    if not lag:
        return date
    result = offset_date(date, lag if is_forward else negate_duration(lag), lag_type, calendar, work_day)
    days, time, months, years = _get_duration_parts(lag)
    if lag_type == "ELAPSEDTIME" or min(days, time / datetime.timedelta(days=1), months, years) >= 0:
        return result  # A positive lag stops at the earliest (forward) or latest (backward) limit
    if is_forward:
        return get_work_finish(result, calendar, work_day)
    return get_work_start(result, calendar, work_day)


def snap_date(
    date: datetime.datetime,
    date_type: Literal["START", "FINISH"],
    calendar: Optional[ifcopenshell.entity_instance],
    work_day: datetime.timedelta = datetime.timedelta(hours=8),
    is_forward: bool = True,
    is_strict: bool = False,
) -> datetime.datetime:
    """Move a start or finish of a task in work time to a work instant

    A start is the instant when the work starts. A finish is the instant when
    the work stops. Out of the work periods, a start moves to the start of the
    next work period and a finish moves to the end of the previous work
    period. For the task, all the instants of a pause in the work are the
    same work instant.

    :param date: The date to move.
    :param date_type: START or FINISH.
    :param calendar: The IfcWorkCalendar of the task, or None.
    :param work_day: The length of a work day of the task.
    :param is_forward: True for the earliest date at or after the date
        (forward pass). False for the latest date at or before the date
        (backward pass).
    :param is_strict: True if the instant itself is a limit, not only the
        work instant: for example after a lag in elapsed time. Forward, a
        finish then moves to the start of the next work period: the work stops
        after that instant. Backward, a start out of the work periods moves to
        the end of the previous work period, and a finish at the start of a
        work period stays there.
    :return: The start or finish.
    """
    start = get_work_start(date, calendar, work_day)
    finish = get_work_finish(date, calendar, work_day)
    if date_type == "START":
        if is_forward or start == date or not is_strict:
            return start
        return finish
    if finish == date:
        return finish
    if is_forward:
        return start if is_strict else finish
    return date if is_strict and start == date else finish


def get_soonest_working_day(start, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance):
    if duration_type == "ELAPSEDTIME" or not is_calendar_applicable(start, calendar):
        return start
    while not is_working_day(start, calendar):
        if not is_calendar_applicable(start, calendar):
            break
        start += datetime.timedelta(days=1)
    return start


def get_recent_working_day(start, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance):
    if duration_type == "ELAPSEDTIME" or not is_calendar_applicable(start, calendar):
        return start
    while not is_working_day(start, calendar):
        if not is_calendar_applicable(start, calendar):
            break
        start -= datetime.timedelta(days=1)
    return start


@cache
def is_working_day(day, calendar: ifcopenshell.entity_instance) -> bool:
    is_working_day = False
    for work_time in calendar.WorkingTimes or []:
        if is_work_time_applicable_to_day(work_time, day):
            is_working_day = True
            break
    if not is_working_day:
        return is_working_day
    for work_time in calendar.ExceptionTimes or []:
        # An exception with time periods removes only these hours, not the day.
        if is_work_time_applicable_to_day(work_time, day) and not get_time_periods(work_time):
            is_working_day = False
            break
    return is_working_day


def get_time_periods(work_time: ifcopenshell.entity_instance) -> list[tuple[datetime.timedelta, datetime.timedelta]]:
    """Get the time periods of a work time

    :param work_time: The IfcWorkTime.
    :return: The sorted (StartTime, EndTime) of each IfcTimePeriod of the
        recurrence pattern, as durations from midnight. An empty list if the
        work time has no time period.
    """
    periods = []
    for period in work_time.RecurrencePattern.TimePeriods or [] if work_time.RecurrencePattern else []:
        periods.append(tuple(get_time_of_day(t) for t in (period.StartTime, period.EndTime)))
    return sorted(periods)


@cache
def get_time_of_day(time: str) -> datetime.timedelta:
    # An IfcTime as a duration from midnight. ISO 8601 24:00:00 is the end of the day.
    if time.startswith("24:00"):
        return datetime.timedelta(days=1)
    t = ifcopenshell.util.date.ifc2datetime(time)
    return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


def get_work_periods(
    day, calendar: Optional[ifcopenshell.entity_instance], work_day: datetime.timedelta = datetime.timedelta(hours=8)
) -> list[tuple[datetime.timedelta, datetime.timedelta]]:
    """Get the work periods of a day

    The work periods are the IfcTimePeriod of the calendar working times that
    apply to the day. If there is no time period, there is one work period
    that starts at 09:00 and lasts the work day. The IfcTimePeriod of the
    calendar exception times that apply to the day are removed.

    :param day: The date or datetime of the day.
    :param calendar: The IfcWorkCalendar, or None.
    :param work_day: The length of the work period if there is no time period.
    :return: The sorted (start, end) of each work period, as durations from
        midnight. An empty list if the day is not a working day.
    """
    if isinstance(day, datetime.datetime):
        day = day.date()
    is_applicable = calendar and is_calendar_applicable(day, calendar)
    if is_applicable and not is_working_day(day, calendar):
        return []
    periods = []
    if is_applicable:
        for work_time in calendar.WorkingTimes:
            if is_work_time_applicable_to_day(work_time, day):
                periods.extend(get_time_periods(work_time))
    if not periods:
        start = min(datetime.timedelta(hours=9), datetime.timedelta(days=1) - work_day)
        periods = [(start, start + work_day)]
    for work_time in calendar.ExceptionTimes or [] if is_applicable else []:
        if is_work_time_applicable_to_day(work_time, day):
            for exception_start, exception_end in get_time_periods(work_time):
                periods = [
                    period
                    for start, end in periods
                    for period in ((start, min(end, exception_start)), (max(start, exception_end), end))
                    if period[0] < period[1]
                ]
    return sorted(periods)


def get_work_day_duration(
    task: ifcopenshell.entity_instance, calendar: Optional[ifcopenshell.entity_instance] = None
) -> datetime.timedelta:
    """Get the nominal length of a work day

    The length is the sum of the IfcTimePeriod of the first calendar working
    time that has time periods. If there is no time period, the length is the
    Pset_WorkControlCommon.WorkDayDuration of the work schedule of the task.
    If there is no value, the length is 8 hours.

    Dates do not use this length if the calendar has time periods: each
    working day has the length of its own work periods (see
    offset_work_days). The nominal length is for a calendar without time
    periods, and for calculations without dates, such as resource work.

    :param task: The IfcTask.
    :param calendar: The IfcWorkCalendar. If None, the calendar of the task.
    :return: The length of a work day.
    """
    calendar = calendar or (derive_calendar(task) if task else None)
    for work_time in calendar.WorkingTimes or [] if calendar else []:
        if periods := get_time_periods(work_time):
            return sum((end - start for start, end in periods), datetime.timedelta())
    while task:
        for rel in task.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                pset = ifcopenshell.util.element.get_pset(rel.RelatingControl, "Pset_WorkControlCommon")
                if pset and pset.get("WorkDayDuration"):
                    return ifcopenshell.util.date.parse_duration(pset["WorkDayDuration"])
                return datetime.timedelta(hours=8)
        task = task.Nests[0].RelatingObject if task.Nests else None
    return datetime.timedelta(hours=8)


def get_work_duration(
    value: str, duration_type: Optional[DURATION_TYPE], work_day: datetime.timedelta = datetime.timedelta(hours=8)
):
    """Read an IfcDuration as work days and work time, for calculations without dates

    For a WORKTIME duration, the date part of the IfcDuration counts work
    days and the time part counts work hours. Work hours of one work day or
    more become work days. For example, PT24H with a work day of 8 hours
    gives 3 work days. Dates count each working day with the length of
    its own work periods: give them the IfcDuration (see offset_date).

    :param value: The IfcDuration.
    :param duration_type: The IfcTaskDurationEnum of the value.
    :param work_day: The length of a work day.
    :return: For ELAPSEDTIME, the duration. For WORKTIME, a duration with
        the work days as days, and the remaining work time (less than one
        work day) as seconds. Years and months do not change.
    """
    duration = ifcopenshell.util.date.parse_duration(value)
    if duration_type == "ELAPSEDTIME" or not duration:
        return duration
    date_part, _, time_part = value.lstrip("-").partition("T")
    date = ifcopenshell.util.date.parse_duration(date_part) if date_part != "P" else datetime.timedelta()
    days = getattr(date, "tdelta", date)
    work = days / datetime.timedelta(days=1) * work_day
    if time_part:
        work += ifcopenshell.util.date.parse_duration("PT" + time_part)
    work_days, rest = divmod(work, work_day)
    result = date - days + datetime.timedelta(days=work_days) + rest
    return -result if value.startswith("-") else result


def get_lag_time(
    lag_time: ifcopenshell.entity_instance,
    task: ifcopenshell.entity_instance,
    predecessor: ifcopenshell.entity_instance,
) -> Optional[str]:
    """Get the IfcLagTime of a sequence as an IfcDuration

    An IfcRatioMeasure is a part of the time of the predecessor, as a
    percentage lag in MS Project. A work day of the predecessor counts as
    its nominal work day (see get_work_day_duration), and an elapsed day as
    24 hours. Thus the lag is a time only: work hours for a WORKTIME lag,
    hours for an ELAPSEDTIME lag. Hours do not become days.

    :param lag_time: The IfcLagTime.
    :param task: The successor IfcTask.
    :param predecessor: The predecessor IfcTask. An IfcRatioMeasure is a
        ratio of its ScheduleDuration.
    :return: The lag as an IfcDuration, or None if there is no lag.
    """
    if lag_time.LagValue.is_a("IfcDuration"):
        value = lag_time.LagValue.wrappedValue
        return value if ifcopenshell.util.date.parse_duration(value) else None
    task_time = predecessor.TaskTime
    if not task_time or not task_time.ScheduleDuration:
        return None
    if task_time.DurationType == "ELAPSEDTIME":
        day = datetime.timedelta(days=1)
    else:
        day = get_work_day_duration(predecessor)
    duration = get_work_duration(task_time.ScheduleDuration, task_time.DurationType, day)
    duration = getattr(duration, "tdelta", duration)
    time = duration.days * day + (duration - datetime.timedelta(days=duration.days))
    return _format_work_duration(0, time * lag_time.LagValue.wrappedValue) if time else None


@cache
def is_calendar_applicable(day, calendar: ifcopenshell.entity_instance) -> bool:
    if not calendar or not calendar.WorkingTimes:
        return False
    is_applicable = False
    for work_time in calendar.WorkingTimes or []:
        if is_day_in_work_time(day, work_time):
            is_applicable = True
            break
    return is_applicable


def is_day_in_work_time(day, work_time: ifcopenshell.entity_instance) -> bool:
    if isinstance(day, datetime.datetime):
        day = datetime.date(day.year, day.month, day.day)
    # 4 IfcWorktime Start (0:00) and 5 IfcWorktime Finish (24:00) are in the work time
    if (start := work_time[4]) and day < ifcopenshell.util.date.ifc2datetime(start):
        return False
    if (finish := work_time[5]) and day > ifcopenshell.util.date.ifc2datetime(finish):
        return False
    return True


def is_work_time_applicable_to_day(work_time: ifcopenshell.entity_instance, day) -> bool:
    if not is_day_in_work_time(day, work_time):
        return False
    if not work_time.RecurrencePattern:
        return True

    if isinstance(day, datetime.datetime):
        day = datetime.date(day.year, day.month, day.day)
    recurrence = work_time.RecurrencePattern
    recurrence_type: RECURRENCE_TYPE = recurrence.RecurrenceType
    if recurrence_type == "DAILY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return True
        # 4 IfcWorktime Start
        if not work_time[4]:
            return False
        return False  # TODO
    elif recurrence_type == "WEEKLY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent
        # 4 IfcWorktime Start
        if not work_time[4]:
            return False
        return False  # TODO
    elif recurrence_type == "MONTHLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence_type == "MONTHLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent and floor(day.day / 7) + 1 == recurrence[
                "Position"
            ]
        return False  # TODO
    elif recurrence_type == "YEARLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.month in recurrence.MonthComponent and day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence_type == "YEARLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (
                day.month in recurrence.MonthComponent
                and (day.weekday() + 1) in recurrence.WeekdayComponent
                and floor(day.day / 7) + 1 == recurrence.Position
            )
        return False  # TODO


def get_task_work_schedule(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    parent_task = get_parent_task(task)
    if parent_task:
        return get_task_work_schedule(parent_task) or get_task_work_schedule(task)
    else:
        for rel in task.HasAssignments:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        return None


def get_nested_tasks(task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [obj for obj in ifcopenshell.util.element.get_components(task) if obj.is_a("IfcTask")]


def get_parent_task(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    nests = task.Nests
    if nests and (obj := nests[0].RelatingObject).is_a("IfcTask"):
        return obj


def get_all_nested_tasks(task: ifcopenshell.entity_instance) -> Generator[ifcopenshell.entity_instance]:
    for nested_task in get_nested_tasks(task):
        yield nested_task
        yield from get_all_nested_tasks(nested_task)


def get_work_schedule_tasks(work_schedule: ifcopenshell.entity_instance) -> Generator[ifcopenshell.entity_instance]:
    """Get all work schedule tasks, including the nested ones."""
    for root_task in get_root_tasks(work_schedule):
        yield root_task
        yield from get_all_nested_tasks(root_task)


def get_root_tasks(work_schedule: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [obj for rel in work_schedule.Controls for obj in rel.RelatedObjects if obj.is_a("IfcTask")]


def guess_date_range(work_schedule: ifcopenshell.entity_instance):
    earliest = None
    latest = None
    root_tasks = get_root_tasks(work_schedule)
    tasks_with_assignements = []
    for task in root_tasks:
        if has_task_outputs(task) or has_task_inputs(task):
            tasks_with_assignements.append(task)
        for sub_task in get_all_nested_tasks(task):
            if has_task_outputs(sub_task) or has_task_inputs(sub_task):
                tasks_with_assignements.append(sub_task)

    for task in tasks_with_assignements:
        derived_start = derive_date(task, "ScheduleStart", is_earliest=True)
        derived_finish = derive_date(task, "ScheduleFinish", is_latest=True)
        if derived_start and (not earliest or derived_start < earliest):
            earliest = derived_start
        if derived_finish and (not latest or derived_finish > latest):
            latest = derived_finish
    return earliest, latest


def get_task_outputs(
    task: ifcopenshell.entity_instance, is_recursive: bool = False
) -> set[ifcopenshell.entity_instance]:
    if is_recursive:
        return {o for subtask in [task] + list(get_all_nested_tasks(task)) for o in get_task_outputs(subtask)}
    return {rel.RelatingProduct for rel in task.HasAssignments if rel.is_a("IfcRelAssignsToProduct")}


def get_task_inputs(
    task: ifcopenshell.entity_instance, is_recursive: bool = False
) -> set[ifcopenshell.entity_instance]:
    if is_recursive:
        return {o for subtask in [task] + list(get_all_nested_tasks(task)) for o in get_task_inputs(subtask)}
    return {o for rel in task.OperatesOn for o in rel.RelatedObjects if o.is_a("IfcProduct")}


def get_task_resources(
    task: ifcopenshell.entity_instance, is_recursive: bool = False
) -> set[ifcopenshell.entity_instance]:
    if is_recursive:
        return {r for subtask in [task] + list(get_all_nested_tasks(task)) for r in get_task_resources(subtask)}
    return {o for rel in task.OperatesOn for o in rel.RelatedObjects if o.is_a("IfcResource")}


def has_task_outputs(task: ifcopenshell.entity_instance) -> bool:
    return len(get_task_outputs(task)) > 0


def has_task_inputs(task: ifcopenshell.entity_instance) -> bool:
    return len(get_task_inputs(task)) > 0


def get_tasks_for_product(
    product: ifcopenshell.entity_instance, schedule: Optional[ifcopenshell.entity_instance] = None
) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
    """
    Get all tasks assigned to or referenced by the given product.

    :param product: An object that is assigned tasks or references tasks.
    :param schedule: An optional string representing the schedule name to filter tasks by.

    :return: A tuple of two lists:
    - The first list contains all tasks assigned to the product.
    - The second list contains all tasks referenced by the product that are part of the given schedule.
    """
    inputs = [
        assignement.RelatingProcess
        for assignement in product.HasAssignments
        if assignement.is_a("IfcRelAssignsToProcess") and assignement.RelatingProcess.is_a("IfcTask")
    ]
    outputs = [
        obj
        for ref in product.ReferencedBy
        if ref.is_a("IfcRelAssignsToProduct")
        for obj in ref.RelatedObjects
        if obj.is_a("IfcTask")
    ]

    if schedule:
        inputs = [task for task in inputs if get_task_work_schedule(task).id() == schedule.id()]
        outputs = [task for task in outputs if get_task_work_schedule(task).id() == schedule.id()]

    return inputs, outputs


def get_sequence_assignment(task: ifcopenshell.entity_instance, sequence="successor"):
    if sequence == "successor":
        relationship_attr = "IsPredecessorTo"
    elif sequence == "predecessor":
        relationship_attr = "IsSuccessorFrom"
    else:
        return []

    relationship = getattr(task, relationship_attr, None)
    if relationship:
        return relationship

    for rel in task.Nests or []:
        result = get_sequence_assignment(rel.RelatingObject, sequence)
        if result:
            return result

    return []


def get_related_products(
    relating_product: Optional[ifcopenshell.entity_instance] = None,
    related_object: Optional[ifcopenshell.entity_instance] = None,
) -> set[ifcopenshell.entity_instance]:
    """Gets the related products being output by a task

    :param relating_product: One of the products already output by the task.
    :param related_object: The IfcTask that you want to get all the related
        products for.
    :return: A set of IfcProducts output by the IfcTask.

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's create a construction task. Note that the predefined type is
        # important to distinguish types of tasks.
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Build wall", identification="A", predefined_type="CONSTRUCTION")

        # Let's say we have a wall somewhere.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's construct that wall!
        ifcopenshell.api.sequence.assign_product(relating_product=wall, related_object=task)

        # This will give us a set with that wall in it.
        products = ifcopenshell.util.sequence.get_related_products(related_object=task)
    """

    assert relating_product or related_object, "Either relating_product or related_object must be provided."

    products = set()
    if not related_object and relating_product:
        for reference in relating_product.ReferencedBy:
            if reference.is_a("IfcRelAssignsToProduct"):
                related_object = reference.RelatedObjects[0]

    if related_object:
        assignments = related_object.HasAssignments
        for assignment in assignments:
            if assignment.is_a("IfcRelAssignsToProduct"):
                products.add(assignment.RelatingProduct.id())

    return products
