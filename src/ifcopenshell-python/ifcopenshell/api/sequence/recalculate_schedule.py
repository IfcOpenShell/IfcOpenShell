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
from typing import Optional

import networkx as nx

import ifcopenshell.api.sequence
import ifcopenshell.util.date
import ifcopenshell.util.sequence


def recalculate_schedule(file: ifcopenshell.file, work_schedule: ifcopenshell.entity_instance) -> None:
    """Calculate the critical path and floats for a work schedule

    This implements critical path analysis, using the forward pass and
    backward pass method. When run, any tasks that have no float will be
    marked as critical, and both the total and free floats will be
    populated for all task times.

    Cyclical relationships are detected and will result in a recursion
    error.

    :param work_schedule: The IfcWorkSchedule to perform the calculation on.
    :return: None

    Example:

    .. code:: python

        # See the example for ifcopenshell.api.sequence.cascade_schedule for
        # details of how to set up a basic set of tasks and calculate the
        # critical path. Typically cascade_schedule is run prior to ensure
        # that dates are correct.
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(work_schedule)


class Usecase:
    file: ifcopenshell.file

    def execute(self, work_schedule: ifcopenshell.entity_instance) -> None:
        self.work_schedule = work_schedule
        # The method implemented is the same as shown here:
        # https://www.youtube.com/watch?v=qTErIV6OqLg
        self.start_dates = []
        self.build_network_graph()

        if not self.start_dates:
            return

        is_cyclic = False
        attempts = 0
        self.pending_nodes = set(self.g.nodes)
        max_worst_case_attempts = pow(len(self.pending_nodes), 2)
        while self.pending_nodes:
            attempts += 1
            remaining_nodes = set()
            for pending_node in self.pending_nodes:
                if not self.forward_pass(pending_node):
                    remaining_nodes.add(pending_node)
            self.pending_nodes = remaining_nodes

            # As we parse nodes, the remaining attempts can drop dramatically, so we recalculate the upper limit
            max_remaining_attempts = pow(len(self.pending_nodes), 2)
            if max_remaining_attempts < max_worst_case_attempts:
                max_worst_case_attempts = max_remaining_attempts
                attempts = 0

            if attempts > max_worst_case_attempts:
                is_cyclic = True
                break  # We have an infinite loop due to a cyclic graph

        if is_cyclic:
            raise RecursionError("Task graph is cyclic and so critical path method cannot be performed.")

        self.pending_nodes = set(self.g.nodes)
        while self.pending_nodes:
            remaining_nodes = set()
            for pending_node in self.pending_nodes:
                if not self.backward_pass(pending_node):
                    remaining_nodes.add(pending_node)
            self.pending_nodes = remaining_nodes

        self.update_task_times()

    def build_network_graph(self) -> None:
        self.sequence_type_map = {
            None: "FS",
            "START_START": "SS",
            "START_FINISH": "SF",
            "FINISH_START": "FS",
            "FINISH_FINISH": "FF",
            "USERDEFINED": "FS",
            "NOTDEFINED": "FS",
        }
        self.g = nx.DiGraph()
        self.edges = []
        no_time, eight_hours = datetime.timedelta(), datetime.timedelta(hours=8)
        self.g.add_node(
            "start", duration=no_time, duration_type="ELAPSEDTIME", calendar=None, work_day=eight_hours, is_virtual=True
        )
        self.g.add_node(
            "finish",
            duration=no_time,
            duration_type="ELAPSEDTIME",
            calendar=None,
            work_day=eight_hours,
            is_virtual=True,
        )
        for rel in self.work_schedule.Controls:
            for related_object in rel.RelatedObjects:
                if not related_object.is_a("IfcTask"):
                    continue
                self.add_node(related_object)
        self.g.add_edges_from(self.edges)

    def add_node(self, task: ifcopenshell.entity_instance) -> None:
        if task.IsNestedBy:
            for rel in task.IsNestedBy:
                [self.add_node(o) for o in rel.RelatedObjects]
            return

        calendar = ifcopenshell.util.sequence.derive_calendar(task)
        work_day = ifcopenshell.util.sequence.get_work_day_duration(task, calendar)
        if task.TaskTime and task.TaskTime.ScheduleDuration:
            duration_type = task.TaskTime.DurationType
            duration = task.TaskTime.ScheduleDuration
            if not ifcopenshell.util.date.parse_duration(duration):
                duration = datetime.timedelta()  # A milestone
        else:
            duration = datetime.timedelta()
            duration_type = "ELAPSEDTIME"

        self.g.add_node(
            task.id(),
            duration=duration,
            duration_type=duration_type,
            calendar=calendar,
            work_day=work_day,
        )

        self.edges.extend(
            [
                (
                    rel.RelatingProcess.id(),
                    task.id(),
                    {
                        "lag_time": (
                            datetime.timedelta()
                            if not rel.TimeLag
                            else ifcopenshell.util.sequence.get_lag_time(rel.TimeLag, task, rel.RelatingProcess)
                        ),
                        "lag_type": rel.TimeLag.DurationType if rel.TimeLag else "WORKTIME",
                        "type": self.sequence_type_map[rel.SequenceType],
                    },
                )
                for rel in ifcopenshell.util.sequence.get_sequence_assignment(task, sequence="predecessor")
            ]
        )

        predecessor_types = [
            rel.SequenceType for rel in ifcopenshell.util.sequence.get_sequence_assignment(task, "predecessor")
        ]
        successor_types = [
            rel.SequenceType for rel in ifcopenshell.util.sequence.get_sequence_assignment(task, "successor")
        ]

        if not predecessor_types:
            self.edges.append(("start", task.id(), {"lag_time": None, "lag_type": "WORKTIME", "type": "FS"}))
            if task.TaskTime and task.TaskTime.ScheduleStart:
                self.start_dates.append(ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleStart))
                # we assume this task is constrained to start on this date
                self.g.nodes[task.id()]["early_start"] = ifcopenshell.util.sequence.snap_task_date(
                    ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleStart),
                    "START",
                    duration,
                    duration_type,
                    calendar,
                    work_day,
                )
        if not successor_types:
            self.edges.append((task.id(), "finish", {"lag_time": None, "lag_type": "WORKTIME", "type": "FF"}))

    def update_task_times(self) -> None:
        for ifc_definition_id in self.g.nodes:
            if ifc_definition_id in ("start", "finish"):
                continue
            data = self.g.nodes[ifc_definition_id]
            task = self.file.by_id(ifc_definition_id)
            if not task.TaskTime:
                continue
            ifcopenshell.api.sequence.edit_task_time(
                self.file,
                task_time=task.TaskTime,
                attributes={
                    "FreeFloat": data["free_float"],
                    "TotalFloat": data["total_float"],
                    "IsCritical": ifcopenshell.util.date.parse_duration(data["total_float"]).days == 0,
                    "EarlyStart": ifcopenshell.util.date.datetime2ifc(data["early_start"], "IfcDateTime"),
                    "EarlyFinish": ifcopenshell.util.date.datetime2ifc(data["early_finish"], "IfcDateTime"),
                    "LateStart": ifcopenshell.util.date.datetime2ifc(data["late_start"], "IfcDateTime"),
                    "LateFinish": ifcopenshell.util.date.datetime2ifc(data["late_finish"], "IfcDateTime"),
                },
            )

    def snap(self, node: dict, date: datetime.datetime, date_type: str):
        # A start moves to the next work instant of the node, a finish to the previous one. A milestone and the
        # start and finish of the network do not move.
        if node.get("is_virtual") or not node["duration"]:
            return date
        calendar, work_day = node["calendar"], node["work_day"]
        if node["duration_type"] == "ELAPSEDTIME":
            calendar, work_day = None, datetime.timedelta(hours=8)  # 09:00 to 17:00, as before
        return ifcopenshell.util.sequence.snap_date(date, date_type, calendar, work_day)

    def get_date(self, node: dict, date: datetime.datetime, date_type: str) -> datetime.datetime:
        # The finish of the node from its start, or the start from its finish.
        return ifcopenshell.util.sequence.get_start_or_finish_date(
            date, node["duration"], node["duration_type"], node["calendar"], date_type, node["work_day"]
        )

    def get_late_finish(self, node: dict, date_type: str, date: datetime.datetime) -> datetime.datetime:
        # The latest finish of the node from a limit of its start or finish. A task of work days uses whole days.
        if date_type == "FINISH":
            return self.get_dates_from_finish(node, date, False)[1]
        return self.get_date(node, date, "FINISH")

    def get_dates_from_finish(self, node: dict, finish: datetime.datetime, is_forward: bool) -> tuple:
        # The start and the finish from a limit of the finish. A task of work days starts at a day start.
        return ifcopenshell.util.sequence.get_task_dates_from_finish(
            finish, node["duration"], node["duration_type"], node["calendar"], node["work_day"], is_forward
        )

    def offset_link(self, date, edge: dict, successor: dict, node: dict, date_type: str, is_forward: bool):
        # The lag is work time of the successor (WORKTIME) or continuous time (ELAPSEDTIME).
        date = ifcopenshell.util.sequence.offset_lag(
            date, edge["lag_time"], edge["lag_type"], successor["calendar"], successor["work_day"], is_forward
        )
        date = self.snap(node, date, date_type)
        # A task of work days starts at the start of a working day and finishes at the end of a working day.
        return ifcopenshell.util.sequence.snap_task_date(
            date, date_type, node["duration"], node["duration_type"], node["calendar"], node["work_day"], is_forward
        )

    def forward_pass(self, node) -> bool:
        data = self.g.nodes[node]
        if node == "start":
            data["early_start"] = min(self.start_dates)
        elif data.get("early_start") is None:  # A task without predecessors keeps its start
            starts, finishes = [], []
            for predecessor in self.g.predecessors(node):
                predecessor_data = self.g.nodes[predecessor]
                edge = self.g[predecessor][node]
                date = predecessor_data.get("early_finish" if edge["type"] in ("FS", "FF") else "early_start")
                if date is None:
                    return False
                date_type = "START" if edge["type"] in ("FS", "SS") else "FINISH"
                dates = starts if date_type == "START" else finishes
                dates.append(self.offset_link(date, edge, data, data, date_type, True))
            start, finish = max(starts, default=None), max(finishes, default=None)
            if finish and (start is None or self.get_date(data, start, "FINISH") <= finish):
                data["early_start"], data["early_finish"] = self.get_dates_from_finish(data, finish, True)
                return True
            data["early_start"] = start
        data["early_finish"] = self.get_date(data, data["early_start"], "FINISH")
        return True

    def get_successor_limits(self, node, successor, is_early: bool) -> Optional[tuple[str, datetime.datetime]]:
        # The latest start or finish of the node that keeps the early (or late) dates of the successor.
        data, successor_data, edge = self.g.nodes[node], self.g.nodes[successor], self.g[node][successor]
        date = successor_data.get(
            ("early_" if is_early else "late_") + ("start" if edge["type"] in ("FS", "SS") else "finish")
        )
        if date is None:
            return None
        date_type = "FINISH" if edge["type"] in ("FS", "FF") else "START"
        return date_type, self.offset_link(date, edge, successor_data, data, date_type, False)

    def backward_pass(self, node) -> bool:
        data = self.g.nodes[node]
        if node == "finish":
            data["late_start"] = data["late_finish"] = data["early_finish"]
            return True
        limits = [self.get_successor_limits(node, successor, False) for successor in self.g.successors(node)]
        if None in limits:
            return False
        start = min((date for date_type, date in limits if date_type == "START"), default=None)
        finish = min((date for date_type, date in limits if date_type == "FINISH"), default=None)
        if start and (finish is None or self.get_date(data, start, "FINISH") < finish):
            data["late_start"], data["late_finish"] = start, self.get_date(data, start, "FINISH")
        else:
            data["late_start"], data["late_finish"] = self.get_dates_from_finish(data, finish, False)

        data["total_float"] = self.get_float(data, data["late_finish"])
        early_limits = [self.get_successor_limits(node, successor, True) for successor in self.g.successors(node)]
        data["free_float"] = self.get_float(
            data, min(self.get_late_finish(data, date_type, date) for date_type, date in early_limits)
        )
        return True

    def get_float(self, data: dict, finish: datetime.datetime) -> str:
        # A float is work time in the calendar of the task, as in P6 and MS Project: the work days and work hours
        # from the early finish to the finish (see get_work_duration_between). Thus 17:00 and 09:00 the next day
        # give no float. A task in elapsed time has a float in elapsed time.
        early_finish = data["early_finish"]
        if data["duration_type"] == "ELAPSEDTIME" and data["duration"]:
            return ifcopenshell.util.date.datetime2ifc(finish - early_finish, "IfcDuration")
        calendar, work_day = data["calendar"], data["work_day"]
        start, end = sorted((early_finish, finish))
        start = ifcopenshell.util.sequence.get_work_start(start, calendar, work_day)
        work = ifcopenshell.util.sequence.get_work_duration_between(start, max(start, end), calendar, work_day)
        return "-" + work if finish < early_finish and work != "P0D" else work
