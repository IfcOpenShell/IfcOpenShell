# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

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

    def cascade_task(self, task, is_first_task=False, task_sequence=None):
        if task_sequence is None:
            task_sequence = []

        if task in task_sequence:
            print("Warning! Recursive sequence is as follows:")
            for i, debug_task in enumerate(task_sequence):
                if i == 0:
                    print("Starting at", debug_task)
                else:
                    print("... is a predecessor to ...", debug_task)
            print("... which is cyclically a predecessor to ...", task)
            raise RecursionError("Recursive tasks found. Could not cascade schedule.")

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
            predecessor_duration = (
                ifcopenshell.util.date.ifc2datetime(
                    predecessor.TaskTime.ScheduleDuration
                )
                if predecessor.TaskTime and predecessor.TaskTime.ScheduleDuration
                else datetime.timedelta()
            )
            if rel.SequenceType == "FINISH_START":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                days = 0 if predecessor_duration.days == 0 else 1
                duration_type = "WORKTIME"
                if rel.TimeLag:
                    days += self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                if days:
                    starts.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                finish, days, duration_type, self.get_calendar(task)
                            ),
                            datetime.time(9),
                        )
                    )
                    starts.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                finish,
                                days,
                                duration_type,
                                self.get_calendar(predecessor),
                            ),
                            datetime.time(9),
                        )
                    )
                else:
                    starts.append(finish)
            elif rel.SequenceType == "START_START":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    starts.append(
                        self.offset_date(
                            start, days, duration_type, self.get_calendar(task)
                        )
                    )
                    starts.append(
                        self.offset_date(
                            start, days, duration_type, self.get_calendar(predecessor)
                        )
                    )
                else:
                    starts.append(start)
            elif rel.SequenceType == "FINISH_FINISH":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                if rel.TimeLag:
                    days = self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                    finishes.append(
                        self.offset_date(
                            finish, days, duration_type, self.get_calendar(task)
                        )
                    )
                    finishes.append(
                        self.offset_date(
                            finish, days, duration_type, self.get_calendar(predecessor)
                        )
                    )
                else:
                    finishes.append(finish)
            elif rel.SequenceType == "START_FINISH":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                days = -1
                duration_type = "WORKTIME"
                if rel.TimeLag:
                    days += self.get_lag_time_days(rel.TimeLag)
                    duration_type = rel.TimeLag.DurationType
                if days or rel.TimeLag:
                    finishes.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                start, days, duration_type, self.get_calendar(task)
                            ),
                            datetime.time(17),
                        )
                    )
                    finishes.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                start,
                                days,
                                duration_type,
                                self.get_calendar(predecessor),
                            ),
                            datetime.time(17),
                        )
                    )
                else:
                    finishes.append(start)

        if starts and finishes:
            start = max(starts)
            finish = max(finishes)
            potential_finish = ifcopenshell.util.sequence.get_start_or_finish_date(
                start,
                duration,
                task.TaskTime.DurationType,
                self.get_calendar(task),
                date_type="FINISH",
            )
            if potential_finish > finish:
                start_ifc = ifcopenshell.util.date.datetime2ifc(start, "IfcDateTime")
                if task.TaskTime.ScheduleStart == start_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleStart = start_ifc
                task.TaskTime.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(
                    potential_finish, "IfcDateTime"
                )
            else:
                finish_ifc = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")
                if task.TaskTime.ScheduleFinish == finish_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleFinish = finish_ifc
                task.TaskTime.ScheduleStart = ifcopenshell.util.date.datetime2ifc(
                    ifcopenshell.util.sequence.get_start_or_finish_date(
                        finish,
                        duration,
                        task.TaskTime.DurationType,
                        self.get_calendar(task),
                        date_type="START",
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
                ifcopenshell.util.sequence.get_start_or_finish_date(
                    finish,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                    date_type="START",
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
                ifcopenshell.util.sequence.get_start_or_finish_date(
                    start,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                    date_type="FINISH",
                ),
                "IfcDateTime",
            )

        for rel in task.IsPredecessorTo:
            self.cascade_task(rel.RelatedProcess, task_sequence=task_sequence + [task])

    def get_lag_time_days(self, lag_time):
        return ifcopenshell.util.date.ifc2datetime(lag_time.LagValue.wrappedValue).days

    def get_calendar(self, task):
        if task.id() not in self.calendar_cache:
            self.calendar_cache[task.id()] = ifcopenshell.util.sequence.derive_calendar(
                task
            )
        return self.calendar_cache[task.id()]

    def offset_date(self, date, days, duration_type, calendar):
        return ifcopenshell.util.sequence.offset_date(
            date, datetime.timedelta(days=days), duration_type, calendar
        )

    def get_task_time_attribute(self, task, attribute):
        if task.TaskTime:
            value = getattr(task.TaskTime, attribute)
            if value:
                return ifcopenshell.util.date.ifc2datetime(value)
