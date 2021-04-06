import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime, timedelta


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "object": None,
            "name":None,
            "recurrence_pattern": None,
            "start": datetime.now(),
            "finish": datetime.now() + timedelta(days=365)
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        working_time = self.file.create_entity("IfcWorkTime", **{
            "Name": self.settings["name"],
            "Start": ifcopenshell.util.date.datetime2ifc(self.settings["start"], "IfcTime"),
            "Finish": ifcopenshell.util.date.datetime2ifc(self.settings["finish"], "IfcTime")
        })

        #TODO Implement user settings for recurrence pattern
        working_time.RecurrencePattern = ifcopenshell.api.run("time.add_recurrence_pattern", self.file)

        if self.settings["object"].is_a('IfcWorkCalendar'):
            if self.settings["object"].WorkingTimes:
                working_times = list(self.settings["object"].WorkingTimes)
                working_times.append(working_time)
                self.settings["object"].WorkingTimes = working_times
            else:
                self.settings["object"].WorkingTimes = [working_time]
        return working_time