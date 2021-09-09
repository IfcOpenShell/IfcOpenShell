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
        self.seconds_per_day = self.calculate_seconds_per_day()
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

    def calculate_seconds_per_day(self):
        default_seconds_per_day = 8 * 60 * 60
        work_schedule = self.get_work_schedule()
        if not work_schedule:
            return default_seconds_per_day
        psets = ifcopenshell.util.element.get_psets(work_schedule)
        if (
            not psets
            or "Pset_WorkControlCommon" not in psets
            or "WorkDayDuration" not in psets["Pset_WorkControlCommon"]
        ):
            return default_seconds_per_day
        work_day_duration = ifcopenshell.util.date.ifc2datetime(psets["Pset_WorkControlCommon"]["WorkDayDuration"])
        return work_day_duration.seconds

    def get_work_schedule(self):
        for rel in self.settings["task"].HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        for rel in self.settings["task"].Nests or []:
            return self.get_work_schedule(rel.RelatingObject)

    def calculate_duration_in_days(self, resource):
        if not resource.Usage or not resource.Usage.ScheduleWork:
            return
        schedule_usage = resource.Usage.ScheduleUsage or 1
        schedule_duration = ifcopenshell.util.date.ifc2datetime(resource.Usage.ScheduleWork)
        schedule_seconds = 0
        if schedule_duration.days:
            schedule_seconds += schedule_duration.days * self.seconds_per_day
        schedule_seconds += schedule_duration.seconds
        return math.ceil((schedule_seconds / self.seconds_per_day) / schedule_usage)
