import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime
from datetime import timedelta


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "recurrence_pattern": None,
            "start_time": None,
            "end_time": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        time_period = self.file.create_entity("IfcTimePeriod")
        time_period.StartTime = ifcopenshell.util.date.datetime2ifc(self.settings["start_time"], "IfcTime")
        time_period.EndTime = ifcopenshell.util.date.datetime2ifc(self.settings["end_time"], "IfcTime")
        time_periods = list(self.settings["recurrence_pattern"].TimePeriods or [])
        time_periods.append(time_period)
        self.settings["recurrence_pattern"].TimePeriods = time_periods
        return time_period
