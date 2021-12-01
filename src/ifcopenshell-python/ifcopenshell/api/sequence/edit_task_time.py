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
        self.task = self.get_task()
        self.calendar = ifcopenshell.util.sequence.derive_calendar(self.task)

        # If the user specifies both an end date and a duration, the duration takes priority
        if (
            self.settings["attributes"].get("ScheduleDuration", None)
            and "ScheduleFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ScheduleFinish"]
        if (
            self.settings["attributes"].get("ActualDuration", None)
            and "ActualFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ActualFinish"]

        duration_type = self.settings["attributes"].get("DurationType", self.settings["task_time"].DurationType)
        if "ScheduleFinish" in self.settings["attributes"]:
            self.settings["attributes"]["ScheduleFinish"] = ifcopenshell.util.sequence.get_soonest_working_day(
                self.settings["attributes"]["ScheduleFinish"], duration_type, self.calendar
            )
        if "ScheduleStart" in self.settings["attributes"]:
            self.settings["attributes"]["ScheduleStart"] = ifcopenshell.util.sequence.get_soonest_working_day(
                self.settings["attributes"]["ScheduleStart"], duration_type, self.calendar
            )

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
            self.calculate_finish()
        elif "ScheduleStart" in self.settings["attributes"].keys() and self.settings["task_time"].ScheduleDuration:
            self.calculate_finish()
        elif "ScheduleFinish" in self.settings["attributes"].keys() and self.settings["task_time"].ScheduleStart:
            self.calculate_duration()

        if self.settings["task_time"].ScheduleDuration and (
            "ScheduleStart" in self.settings["attributes"].keys()
            or "ScheduleFinish" in self.settings["attributes"].keys()
            or "ScheduleDuration" in self.settings["attributes"].keys()
        ):
            ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=self.task)

    def calculate_finish(self):
        finish_date = ifcopenshell.util.sequence.get_finish_date(
            ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleStart),
            ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleDuration),
            self.settings["task_time"].DurationType,
            self.calendar,
        )
        self.settings["task_time"].ScheduleFinish = ifcopenshell.util.date.datetime2ifc(finish_date, "IfcDateTime")

    def calculate_duration(self):
        start = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleStart)
        finish = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleFinish)
        current_date = datetime.date(start.year, start.month, start.day)
        finish_date = datetime.date(finish.year, finish.month, finish.day)
        duration = datetime.timedelta()
        while current_date < finish_date:
            if self.settings["task_time"].DurationType == "ELAPSEDTIME" or not self.calendar:
                duration += datetime.timedelta(days=1)
            elif ifcopenshell.util.sequence.is_working_day(current_date, self.calendar):
                duration += datetime.timedelta(days=1)
            current_date += datetime.timedelta(days=1)
        self.settings["task_time"].ScheduleDuration = ifcopenshell.util.date.datetime2ifc(duration, "IfcDuration")

    def get_task(self):
        return [e for e in self.file.get_inverse(self.settings["task_time"]) if e.is_a("IfcTask")][0]
