import datetime
import ifcopenshell.util.date
import ifcopenshell.util.sequence


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"task_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # If the user specifies both an end date and a duration, the duration takes priority
        if "ScheduleDuration" in self.settings["attributes"].keys() and "ScheduleFinish" in self.settings["attributes"].keys():
            del self.settings["attributes"]["ScheduleFinish"]
        if "ActualDuration" in self.settings["attributes"].keys() and "ActualFinish" in self.settings["attributes"].keys():
            del self.settings["attributes"]["ActualFinish"]

        for name, value in self.settings["attributes"].items():
            if value:
                if "Start" in name or "Finish" in name or name == "StatusTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
                elif name == "ScheduleDuration" or name == "ActualDuration" or name == "RemainingTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
            setattr(self.settings["task_time"], name, value)

        if (
            "ScheduleDuration" in self.settings["attributes"].keys()
            and self.settings["task_time"].ScheduleDuration
            and self.settings["task_time"].ScheduleStart
        ):
            start = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleStart)
            current_date = datetime.date(start.year, start.month, start.day)
            duration = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleDuration).days

            task = [e for e in self.file.get_inverse(self.settings["task_time"]) if e.is_a("IfcTask")]
            if not task:
                return
            else:
                task = task[0]

            calendar = ifcopenshell.util.sequence.derive_calendar(task)

            while duration >= 0:
                if self.settings["task_time"].DurationType == "ELAPSEDTIME" or not calendar:
                    duration -= 1
                elif ifcopenshell.util.sequence.is_working_day(current_date, calendar):
                    duration -= 1
                current_date += datetime.timedelta(days=1)

            current_date -= datetime.timedelta(days=1)
            self.settings["task_time"].ScheduleFinish = ifcopenshell.util.date.datetime2ifc(current_date, "IfcDateTime")
