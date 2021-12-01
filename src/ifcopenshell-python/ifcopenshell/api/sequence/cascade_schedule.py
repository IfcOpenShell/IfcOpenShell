import datetime
import ifcopenshell.util.date
import ifcopenshell.util.sequence


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"task": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.calendar_cache = {}
        self.cascade_task(self.settings["task"], is_first_task=True)

    def cascade_task(self, task, is_first_task=False):
        if not task.TaskTime:
            return

        duration = (
            ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration)
            if task.TaskTime.ScheduleDuration
            else datetime.timedelta()
        )

        finishes = []
        starts = []

        for rel in task.IsSuccessorFrom:
            predecessor = rel.RelatingProcess
            if rel.SequenceType == "FINISH_START":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    starts.append(self.offset_date(finish, days, duration_type, self.get_calendar(task)))
                    starts.append(self.offset_date(finish, days, duration_type, self.get_calendar(predecessor)))
                else:
                    starts.append(finish)
            elif rel.SequenceType == "START_START":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    starts.append(self.offset_date(start, days, duration_type, self.get_calendar(task)))
                    starts.append(self.offset_date(start, days, duration_type, self.get_calendar(predecessor)))
                else:
                    starts.append(start)
            elif rel.SequenceType == "FINISH_FINISH":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    finishes.append(self.offset_date(finish, days, duration_type, self.get_calendar(task)))
                    finishes.append(self.offset_date(finish, days, duration_type, self.get_calendar(predecessor)))
                else:
                    finishes.append(finish)
            elif rel.SequenceType == "START_FINISH":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    finishes.append(self.offset_date(start, days, duration_type, self.get_calendar(task)))
                    finishes.append(self.offset_date(start, days, duration_type, self.get_calendar(predecessor)))
                else:
                    finishes.append(start)

        if starts and finishes:
            start = max(starts)
            finish = max(finishes)
            potential_finish = datetime.datetime.combine(
                ifcopenshell.util.sequence.get_finish_date(
                    start,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                ),
                datetime.datetime.min.time(),
            )
            if potential_finish > finish:
                start_ifc = ifcopenshell.util.date.datetime2ifc(start, "IfcDateTime")
                if task.TaskTime.ScheduleStart == start_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleStart = start_ifc
                task.TaskTime.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(potential_finish, "IfcDateTime")
            else:
                finish_ifc = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")
                if task.TaskTime.ScheduleFinish == finish_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleFinish = finish_ifc
                task.TaskTime.ScheduleStart = ifcopenshell.util.date.datetime2ifc(
                    ifcopenshell.util.sequence.get_finish_date(
                        finish,
                        -duration,
                        task.TaskTime.DurationType,
                        self.get_calendar(task),
                    ),
                    "IfcDateTime",
                )
        elif finishes:
            finish = max(finishes)
            finish_ifc = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")
            if task.TaskTime.ScheduleFinish == finish_ifc and not is_first_task:
                return
            task.TaskTime.ScheduleFinish = finish_ifc
            task.TaskTime.ScheduleStart = ifcopenshell.util.date.datetime2ifc(
                ifcopenshell.util.sequence.get_finish_date(
                    finish,
                    -duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                ),
                "IfcDateTime",
            )
        elif starts:
            start = max(starts)
            start_ifc = ifcopenshell.util.date.datetime2ifc(start, "IfcDateTime")
            if task.TaskTime.ScheduleStart == start_ifc and not is_first_task:
                return
            task.TaskTime.ScheduleStart = start_ifc
            task.TaskTime.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(
                ifcopenshell.util.sequence.get_finish_date(
                    start,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                ),
                "IfcDateTime",
            )

        for rel in task.IsPredecessorTo:
            self.cascade_task(rel.RelatedProcess)

    def get_lag_time_days(self, lag_time):
        return ifcopenshell.util.date.ifc2datetime(lag_time.LagValue.wrappedValue).days

    def get_calendar(self, task):
        if task.id() not in self.calendar_cache:
            self.calendar_cache[task.id()] = ifcopenshell.util.sequence.derive_calendar(task)
        return self.calendar_cache[task.id()]

    def offset_date(self, date, days, duration_type, calendar):
        return datetime.datetime.combine(
            ifcopenshell.util.sequence.get_finish_date(date, datetime.timedelta(days=days), duration_type, calendar),
            datetime.datetime.min.time(),
        )

    def get_task_time_attribute(self, task, attribute):
        if task.TaskTime:
            value = getattr(task.TaskTime, attribute)
            if value:
                return ifcopenshell.util.date.ifc2datetime(value)
