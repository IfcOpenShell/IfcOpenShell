import ifcopenshell.util.date
from datetime import datetime
from datetime import timedelta

class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "task": None,
            "name": "Unnamed",
            "duration_type": "NOTDEFINED",
            "schedule_duration": None,
            "schedule_start_time": datetime.now(),
            "schedule_finish_time": datetime.now() + timedelta(days=5),
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        task_time = self.file.create_entity("IfcTaskTime", **{"Name": self.settings["name"]})
        task_time.DurationType = self.settings["duration_type"]
        task_time.ScheduleStart = ifcopenshell.util.date.datetime2ifc(self.settings["schedule_start_time"], "IfcDateTime")
        duration = self.settings["schedule_duration"]
        if duration:
            task_time.ScheduleDuration = ifcopenshell.util.date.datetime2ifc(duration, "IfcTime")
            task_time.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(
            self.settings["schedule_start"] + duration,
            "IfcDateTime"
            )
        else:
            duration = self.settings["schedule_finish_time"] - self.settings["schedule_start_time"]
            # task_time.ScheduleDuration = ifcopenshell.util.date.datetime2ifc(duration.days, "IfcTime")
            task_time.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(self.settings["schedule_finish_time"], "IfcDateTime")
        task = self.settings["task"]
        if task:
            task.TaskTime = task_time
        return task_time
