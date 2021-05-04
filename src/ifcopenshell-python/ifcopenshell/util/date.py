import datetime
from re import findall

# https://gist.github.com/spatialtime/c1924a3b178b4fe721fe406e0bf1a1dc
import re
from datetime import timedelta


def format_duration(td):
    s = td.seconds
    ms = td.microseconds
    if ms != 0:  # Round microseconds to milliseconds.
        ms /= 1000000
        ms = round(ms,3)
        s += ms
    return "P{}DT{}S".format(td.days,s)

def parse_duration(iso_duration):
    m = re.match(r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:.\d+)?)S)?$',
        iso_duration)
    if m is None:
        raise ValueError("invalid ISO 8601 duration string")
    days = 0
    hours = 0
    minutes = 0
    seconds = 0.0
    if m[3]:
        days = int(m[3])
    if m[4]:
        hours = int(m[4])
    if m[5]:
        minutes = int(m[5])
    if m[6]:
        seconds = float(m[6])
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def duration2dict(duration):
    results = {}
    for number, unit in findall("(?P<number>\d+)(?P<period>S|M|H|D|W|Y)", duration):
        results[unit] = number
    return results


def ifc2datetime(element):
    if isinstance(element, str) and element[0] == "P":  # IfcDuration
        return parse_duration(element)
    elif isinstance(element, str) and element[2] == ":":  # IfcTime
        return datetime.time.fromisoformat(element)
    elif isinstance(element, str) and ":" in element:  # IfcDateTime
        return datetime.datetime.fromisoformat(element)
    elif isinstance(element, str):  # IfcDate
        return datetime.date.fromisoformat(element)
    elif isinstance(element, int):  # IfcTimeStamp
        return datetime.datetime.fromtimestamp(element)
    elif element.is_a("IfcDateAndTime"):
        return datetime.datetime(
            element.DateComponent.YearComponent,
            element.DateComponent.MonthComponent,
            element.DateComponent.DayComponent,
            element.TimeComponent.HourComponent,
            element.TimeComponent.MinuteComponent,
            element.TimeComponent.SecondComponent,
            # TODO: implement TimeComponent timezone
        )
    elif element.is_a("IfcCalendarDate"):
        return datetime.date(
            element.YearComponent,
            element.MonthComponent,
            element.DayComponent,
        )


def datetime2ifc(dt, ifc_type):
    if isinstance(dt, str) and ifc_type != "IfcDuration":
        dt = datetime.datetime.fromisoformat(dt)
    if ifc_type == "IfcDuration":
        return format_duration(dt)
    if ifc_type == "IfcTimeStamp":
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
        return {"DayComponent": dt.day, "MonthComponent": dt.month, "YearComponent": dt.year}
    elif ifc_type == "IfcLocalTime":
        # TODO implement timezones
        return {"HourComponent": dt.hour, "MinuteComponent": dt.minute, "SecondComponent": dt.second}
