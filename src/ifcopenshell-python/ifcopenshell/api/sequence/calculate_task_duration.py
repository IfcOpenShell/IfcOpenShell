import math
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"task": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.seconds_per_workday = self.calculate_seconds_per_workday()
        duration = self.calculate_max_resource_usage_duration()
        if duration:
            self.set_task_duration(duration)

    def calculate_max_resource_usage_duration(self):
        max_duration = 0
        for rel in self.settings["task"].OperatesOn or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcConstructionResource"):
                    duration = self.calculate_duration_in_days(related_object)
                    if duration and duration > max_duration:
                        max_duration = duration
        return max_duration

    def set_task_duration(self, duration):
        if not self.settings["task"].TaskTime:
            ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.settings["task"])
        self.settings["task"].TaskTime.ScheduleDuration = f"P{duration}D"

    def calculate_seconds_per_workday(self):
        default_seconds_per_workday = 8 * 60 * 60
        work_schedule = self.get_work_schedule(self.settings["task"])
        if not work_schedule:
            return default_seconds_per_workday
        psets = ifcopenshell.util.element.get_psets(work_schedule)
        if (
            not psets
            or "Pset_WorkControlCommon" not in psets
            or "WorkDayDuration" not in psets["Pset_WorkControlCommon"]
        ):
            return default_seconds_per_workday
        work_day_duration = ifcopenshell.util.date.ifc2datetime(psets["Pset_WorkControlCommon"]["WorkDayDuration"])
        return work_day_duration.seconds

    def get_work_schedule(self, task):
        for rel in task.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        for rel in task.Nests or []:
            return self.get_work_schedule(rel.RelatingObject)

    def calculate_duration_in_days(self, resource):
        if not resource.Usage or not resource.Usage.ScheduleWork:
            return
        schedule_usage = resource.Usage.ScheduleUsage or 1
        schedule_duration = ifcopenshell.util.date.ifc2datetime(resource.Usage.ScheduleWork)
        if self.is_hourly_work(resource.Usage.ScheduleWork):
            schedule_seconds = (schedule_duration.days * 24 * 60 * 60) + schedule_duration.seconds
        else:
            partial_days = schedule_duration.seconds / (24 * 60 * 60)
            schedule_seconds = (schedule_duration.days + partial_days) * self.seconds_per_workday
        return math.ceil((schedule_seconds / self.seconds_per_workday) / schedule_usage)

    def is_hourly_work(self, schedule_work):
        return "T" in schedule_work
