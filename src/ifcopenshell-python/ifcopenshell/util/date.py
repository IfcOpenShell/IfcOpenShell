from re import findall
from datetime import datetime


def duration2dict(duration):
    results = {}
    for number, unit in findall("(?P<number>\d+)(?P<period>S|M|H|D|W|Y)", duration):
        results[unit] = number
    return results


def ifc2datetime(element):
    if isinstance(element, str) and element[0] == "P":  # IfcDuration
        return duration2dict(element)
    elif isinstance(element, str):  # IfcDateTime, IfcDate
        return datetime.fromisoformat(element)
    elif isinstance(element, int):  # IfcTimeStamp
        return datetime.fromtimestamp(element)
    elif element.is_a("IfcDateAndTime"):
        return datetime(
            element.DateComponent.YearComponent,
            element.DateComponent.MonthComponent,
            element.DateComponent.DayComponent,
            element.TimeComponent.HourComponent,
            element.TimeComponent.MinuteComponent,
            element.TimeComponent.SecondComponent,
            # TODO: implement TimeComponent timezone
        )
    elif element.is_a("IfcCalendarDate"):
        return datetime(
            element.YearComponent,
            element.MonthComponent,
            element.DayComponent,
        )


def datetime2ifc(dt, ifc_type):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if ifc_type == "IfcTimeStamp":
        return int(dt.timestamp())
    elif ifc_type == "IfcDateTime":
        return dt.isoformat()
    elif ifc_type == "IfcDate":
        return dt.date().isoformat()
    elif ifc_type == "IfcTime":
        return dt.time().isoformat()
    elif ifc_type == "IfcCalendarDate":
        return {"DayComponent": dt.day, "MonthComponent": dt.month, "YearComponent": dt.year}
    elif ifc_type == "IfcLocalTime":
        # TODO implement timezones
        return {"HourComponent": dt.hour, "MinuteComponent": dt.minute, "SecondComponent": dt.second}
