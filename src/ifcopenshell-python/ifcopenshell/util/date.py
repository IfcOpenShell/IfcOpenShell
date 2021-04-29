import datetime
from re import findall


def duration2dict(duration):
    results = {}
    for number, unit in findall("(?P<number>\d+)(?P<period>S|M|H|D|W|Y)", duration):
        results[unit] = number
    return results


def ifc2datetime(element):
    if isinstance(element, str) and element[0] == "P":  # IfcDuration
        return duration2dict(element)
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
    if isinstance(dt, str):
        dt = datetime.datetime.fromisoformat(dt)
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
