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

import ifcopenshell
import datetime
import isodate
from re import findall
from dateutil import parser
from typing import Literal, Union, Any, overload


def timedelta2duration(timedelta):
    components = {
        "days": getattr(timedelta, "days", 0),
        "hours": 0,
        "minutes": 0,
        "seconds": getattr(timedelta, "seconds", 0),
    }
    if components["seconds"]:
        components["hours"], components["minutes"], components["seconds"] = [
            int(i) for i in str(datetime.timedelta(seconds=components["seconds"])).split(":")
        ]
    return isodate.Duration(**components)


def ifc2datetime(element: Union[str, int, ifcopenshell.entity_instance]):
    if isinstance(element, str):
        if "P" in element[0:2]:  # IfcDuration
            duration = parse_duration(element)
            if isinstance(duration, datetime.timedelta):
                return timedelta2duration(duration)
            return duration
        elif len(element) > 3 and element[2] == ":":  # IfcTime
            return datetime.time.fromisoformat(element)
        elif ":" in element:  # IfcDateTime
            return datetime.datetime.fromisoformat(element)
        else:  # IfcDate
            return datetime.date.fromisoformat(element)

    elif isinstance(element, int):  # IfcTimeStamp
        return datetime.datetime.fromtimestamp(element)

    elif isinstance(element, ifcopenshell.entity_instance):
        if element.is_a("IfcDateAndTime"):
            return datetime.datetime(
                element.DateComponent.YearComponent,
                element.DateComponent.MonthComponent,
                element.DateComponent.DayComponent,
                element.TimeComponent.HourComponent,
                element.TimeComponent.MinuteComponent,
                int(element.TimeComponent.SecondComponent),
                # TODO: implement TimeComponent timezone
            )
        elif element.is_a("IfcCalendarDate"):
            return datetime.date(
                element.YearComponent,
                element.MonthComponent,
                element.DayComponent,
            )


def readable_ifc_duration(duration: str) -> str:
    """Convert ISO duration to more readable string format.

    Examples:
    - "P2Y3M1W4DT5H45M30S" -> "2 Y 3 M 1 W 4 D 5 h 45 m 30 s"
    - "P2Y3MT30S" -> "2 Y 3 M 30 s"
    - "PT2500H" -> "2500 h" (hours are not converted to days)
    """
    # NOTE: we don't use isodate.parseduration as it's going to
    # represent "PT2500H" as "12w 6d 4h", though user may want
    # intentionally to use just hours.

    if "T" in duration:
        period_duration, time_duration = duration.split("T")
        period_duration = period_duration[1:]
    else:
        period_duration = duration[1:]
        time_duration = ""

    result: list[str] = []
    for designator in ("Y", "M", "W", "D"):
        if designator in period_duration:
            value, period_duration = period_duration.split(designator)
            if float(value):
                result.append(f"{value}{designator}")

    if time_duration:
        for designator in ("H", "M", "S"):
            if designator in time_duration:
                value, time_duration = time_duration.split(designator)
                if float(value):
                    result.append(f"{value}{designator.lower()}")
    return " ".join(result)


@overload
def datetime2ifc(dt: None, ifc_type: Any) -> None: ...
@overload
def datetime2ifc(
    dt: Union[datetime.date, str, None],
    ifc_type: Literal[
        "IfcDuration",
        "IfcTimeStamp",
        "IfcDateTime",
        "IfcDate",
        "IfcTime",
        "IfcCalendarDate",
        "IfcLocalTime",
    ],
) -> Union[int, str, dict[str, Any], None]: ...
def datetime2ifc(
    dt: Union[datetime.date, str, None],
    ifc_type: Literal[
        "IfcDuration",
        "IfcTimeStamp",
        "IfcDateTime",
        "IfcDate",
        "IfcTime",
        "IfcCalendarDate",
        "IfcLocalTime",
    ],
) -> Union[int, str, dict[str, Any], None]:
    if isinstance(dt, str):
        if ifc_type == "IfcDuration":
            return dt
        try:
            dt = datetime.datetime.fromisoformat(dt)
        except:
            dt = datetime.time.fromisoformat(dt)
    elif dt is None:
        return

    if ifc_type == "IfcDuration":
        return isodate.duration_isoformat(dt)
    elif ifc_type == "IfcTimeStamp":
        return int(dt.timestamp())
    elif ifc_type == "IfcDateTime":
        if isinstance(dt, datetime.datetime):
            return dt.isoformat()
        elif isinstance(dt, datetime.date):
            return datetime.datetime.combine(dt, datetime.datetime.min.time()).isoformat()
    elif ifc_type == "IfcDate":
        if isinstance(dt, datetime.datetime):
            return dt.date().isoformat()
        elif isinstance(dt, datetime.date):
            return dt.isoformat()
    elif ifc_type == "IfcTime":
        if isinstance(dt, datetime.datetime):
            return dt.time().isoformat()
        elif isinstance(dt, datetime.time):
            return dt.isoformat()
    elif ifc_type == "IfcCalendarDate":
        return {
            "DayComponent": dt.day,
            "MonthComponent": dt.month,
            "YearComponent": dt.year,
        }
    elif ifc_type == "IfcLocalTime":
        # TODO implement timezones
        return {
            "HourComponent": dt.hour,
            "MinuteComponent": dt.minute,
            "SecondComponent": dt.second,
        }

    raise TypeError(f"Unsupported ifc_type for conversion from datetime.datetime = {ifc_type}, value = {dt}")


def string_to_date(string):
    if not string:
        return None
    try:
        return parser.isoparse(string)
    except:
        try:
            return parser.parse(string, dayfirst=True, fuzzy=True)
        except:
            return None


def string_to_duration(duration_string):
    # TODO support years, months, weeks aswell
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    match = findall(r"(\d+\.?\d*)d", duration_string)
    if match:
        days = float(match[0])
    match = findall(r"(\d+\.?\d*)h", duration_string)
    if match:
        hours = float(match[0])
    match = findall(r"(\d+\.?\d*)m", duration_string)
    if match:
        minutes = float(match[0])
    match = findall(r"(\d+\.?\d*)s", duration_string)
    if match:
        seconds = float(match[0])
    return isodate.duration_isoformat(datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))


def parse_duration(value: Union[str, None]) -> Union[datetime.timedelta, None]:
    if not value:
        return None
    if isinstance(value, str):
        if "P" in value:
            try:
                return isodate.parse_duration(value)
            except:
                print("Error parsing ISO string duration")
            return None
        else:
            try:
                final_string = "P"
                value_upper = value.upper()
                for char in value_upper:
                    if char.isdigit():
                        final_string += char
                    elif char == "D":
                        final_string += "D"
                        if "H" in value_upper or "S" in value_upper or "MIN" in value_upper:
                            final_string += "T"
                    elif char == "W":
                        final_string += "W"
                    elif char == "M":
                        final_string += "M"
                    elif char == "Y":
                        final_string += "Y"
                    elif char == "H":
                        final_string = (
                            final_string[:1] + "T" + final_string[1:] if "T" not in final_string else final_string
                        )
                        final_string += "H"
                    elif char == "M":
                        if "MIN" in value_upper and "T" not in final_string:
                            final_string = final_string[:1] + "T" + final_string[1:]
                        final_string += "M"
                    elif char == "S":
                        final_string = (
                            final_string[:1] + "T" + final_string[1:] if "T" not in final_string else final_string
                        )
                        final_string += "S"
                return isodate.parse_duration(final_string)
            except:
                print("error fuzzy parsing duration")
                return None


def canonicalise_time(time: Union[datetime.datetime, None]) -> str:
    if not time:
        return "-"
    return time.strftime("%d/%m/%y")
