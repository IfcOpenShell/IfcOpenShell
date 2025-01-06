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
    :type work_schedule: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # See the example for ifcopenshell.api.sequence.cascade_schedule for
        # details of how to set up a basic set of tasks and calculate the
        # critical path. Typically cascade_schedule is run prior to ensure
        # that dates are correct.
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"work_schedule": work_schedule}
    return usecase.execute()


class Usecase:
    def execute(self):
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
            return

        self.pending_nodes = set(self.g.nodes)
        while self.pending_nodes:
            remaining_nodes = set()
            for pending_node in self.pending_nodes:
                if not self.backward_pass(pending_node):
                    remaining_nodes.add(pending_node)
            self.pending_nodes = remaining_nodes

        self.update_task_times()

    def build_network_graph(self):
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
        self.g.add_node("start", duration=0, duration_type="ELAPSEDTIME", calendar=None)
        self.g.add_node("finish", duration=0, duration_type="ELAPSEDTIME", calendar=None)
        for rel in self.settings["work_schedule"].Controls:
            for related_object in rel.RelatedObjects:
                if not related_object.is_a("IfcTask"):
                    continue
                self.add_node(related_object)
        self.g.add_edges_from(self.edges)

    def add_node(self, task):
        if task.IsNestedBy:
            for rel in task.IsNestedBy:
                [self.add_node(o) for o in rel.RelatedObjects]
            return

        if task.TaskTime and task.TaskTime.ScheduleDuration:
            duration = ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration).days
            duration_type = task.TaskTime.DurationType
        else:
            duration = 0
            duration_type = "ELAPSEDTIME"

        self.g.add_node(
            task.id(),
            duration=duration,
            duration_type=duration_type,
            calendar=ifcopenshell.util.sequence.derive_calendar(task),
        )

        self.edges.extend(
            [
                (
                    rel.RelatingProcess.id(),
                    task.id(),
                    {
                        "lag_time": (
                            0
                            if not rel.TimeLag
                            else ifcopenshell.util.date.ifc2datetime(rel.TimeLag.LagValue.wrappedValue).days
                        ),
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
            self.edges.append(("start", task.id(), {"lag_time": 0, "type": "FS"}))
            if task.TaskTime and task.TaskTime.ScheduleStart:
                self.start_dates.append(ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleStart))
                self.g.nodes[task.id()]["early_start"] = ifcopenshell.util.date.ifc2datetime(
                    task.TaskTime.ScheduleStart
                )  # we assume this task is constrained to start on this date
        if not successor_types:
            self.edges.append((task.id(), "finish", {"lag_time": 0, "type": "FF"}))

    def update_task_times(self):
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
                    "FreeFloat": ifcopenshell.util.date.datetime2ifc(data["free_float"], "IfcDuration"),
                    "TotalFloat": ifcopenshell.util.date.datetime2ifc(data["total_float"], "IfcDuration"),
                    "IsCritical": data["total_float"].days == 0,
                    "EarlyStart": ifcopenshell.util.date.datetime2ifc(data["early_start"], "IfcDateTime"),
                    "EarlyFinish": ifcopenshell.util.date.datetime2ifc(data["early_finish"], "IfcDateTime"),
                    "LateStart": ifcopenshell.util.date.datetime2ifc(data["late_start"], "IfcDateTime"),
                    "LateFinish": ifcopenshell.util.date.datetime2ifc(data["late_finish"], "IfcDateTime"),
                },
            )

    def offset_date(self, date, days, node):
        return ifcopenshell.util.sequence.offset_date(
            date, datetime.timedelta(days=days), node["duration_type"], node["calendar"]
        )

    def forward_pass(self, node):
        successors = self.g.successors(node)
        predecessors = list(self.g.predecessors(node))
        data = self.g.nodes[node]

        if node == "start":
            data["early_start"] = min(self.start_dates)
        else:
            finishes = []
            starts = []
            if data.get("early_start") is not None:
                data["early_finish"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                    data["early_start"],
                    datetime.timedelta(days=data["duration"]),
                    data["duration_type"],
                    data["calendar"],
                    date_type="FINISH",
                )
                return True  # we're done! We assume this task is constrained and finish processing it

            for predecessor in predecessors:
                predecessor_data = self.g.nodes[predecessor]
                edge = self.g[predecessor][node]
                if edge["type"] == "FS":
                    finish = predecessor_data.get("early_finish")
                    if finish is None:
                        return
                    days = 0 if predecessor_data["duration"] == 0 else 1
                    if edge["lag_time"]:
                        days += edge["lag_time"]
                    if days:
                        starts.append(datetime.datetime.combine(self.offset_date(finish, days, data), datetime.time(9)))
                        starts.append(
                            datetime.datetime.combine(
                                self.offset_date(finish, days, predecessor_data),
                                datetime.time(9),
                            )
                        )
                    else:
                        starts.append(finish)
                elif edge["type"] == "SS":
                    start = predecessor_data.get("early_start")
                    if start is None:
                        return
                    if edge["lag_time"]:
                        starts.append(self.offset_date(start, edge["lag_time"], data))
                        starts.append(self.offset_date(start, edge["lag_time"], predecessor_data))
                    else:
                        starts.append(start)
                elif edge["type"] == "FF":
                    finish = predecessor_data.get("early_finish")
                    if finish is None:
                        return
                    if edge["lag_time"]:
                        finishes.append(self.offset_date(finish, edge["lag_time"], data))
                        finishes.append(self.offset_date(finish, edge["lag_time"], predecessor_data))
                    else:
                        finishes.append(finish)
                elif edge["type"] == "SF":
                    start = predecessor_data.get("early_start")
                    if start is None:
                        return
                    days = -1
                    if edge["lag_time"]:
                        days += edge["lag_time"]
                    if days or edge["lag_time"]:
                        finishes.append(
                            datetime.datetime.combine(self.offset_date(start, days, data), datetime.time(17))
                        )
                        finishes.append(
                            datetime.datetime.combine(
                                self.offset_date(start, days, predecessor_data),
                                datetime.time(17),
                            )
                        )
                    else:
                        finishes.append(start)
            if starts and finishes:
                data["early_start"] = max(starts)
                data["early_finish"] = max(finishes)
                potential_finish = ifcopenshell.util.sequence.get_start_or_finish_date(
                    data["early_start"],
                    datetime.timedelta(days=data["duration"]),
                    data["duration_type"],
                    data["calendar"],
                    date_type="FINISH",
                )
                if potential_finish > data["early_finish"]:
                    data["early_finish"] = potential_finish
                else:
                    data["early_start"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                        data["early_finish"],
                        datetime.timedelta(days=data["duration"]),
                        data["duration_type"],
                        data["calendar"],
                        date_type="START",
                    )
            elif finishes:
                data["early_finish"] = max(finishes)
            elif starts:
                data["early_start"] = max(starts)
            else:
                print("How did this happen?")

        if data.get("early_finish") is None:
            data["early_finish"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                data["early_start"],
                datetime.timedelta(days=data["duration"]),
                data["duration_type"],
                data["calendar"],
                date_type="FINISH",
            )
        elif data.get("early_start") is None:
            data["early_start"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                data["early_finish"],
                datetime.timedelta(days=data["duration"]),
                data["duration_type"],
                data["calendar"],
                date_type="START",
            )

        return True

    def backward_pass(self, node):
        successors = list(self.g.successors(node))
        predecessors = self.g.predecessors(node)
        data = self.g.nodes[node]
        free_floats = []

        if node == "finish":
            data["late_finish"] = data["early_finish"]
        else:
            finishes = []
            starts = []
            for successor in successors:
                successor_data = self.g.nodes[successor]
                edge = self.g[node][successor]
                if edge["type"] == "FS":
                    start = successor_data.get("late_start")
                    if start is None:
                        return
                    days = 1
                    if edge["lag_time"]:
                        days += edge["lag_time"]
                    if days or edge["lag_time"]:
                        finishes.append(
                            datetime.datetime.combine(self.offset_date(start, -days, data), datetime.time(17))
                        )
                        finishes.append(
                            datetime.datetime.combine(
                                self.offset_date(start, -days, successor_data),
                                datetime.time(17),
                            )
                        )
                    else:
                        finishes.append(start)
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_finish"].date() + datetime.timedelta(days=1),
                            successor_data["early_start"].date(),
                            edge["lag_time"],
                            data,
                            successor_data,
                        )
                    )
                elif edge["type"] == "SS":
                    start = successor_data.get("late_start")
                    if start is None:
                        return
                    if edge["lag_time"]:
                        starts.append(self.offset_date(start, -edge["lag_time"], data))
                        starts.append(self.offset_date(start, -edge["lag_time"], successor_data))
                    else:
                        starts.append(start)
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_start"],
                            successor_data["early_start"],
                            edge["lag_time"],
                            data,
                            successor_data,
                        )
                    )
                elif edge["type"] == "FF":
                    finish = successor_data.get("late_finish")
                    if finish is None:
                        return
                    if edge["lag_time"]:
                        finishes.append(self.offset_date(finish, -edge["lag_time"], data))
                        finishes.append(self.offset_date(finish, -edge["lag_time"], successor_data))
                    else:
                        finishes.append(finish)
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_finish"],
                            successor_data["early_finish"],
                            edge["lag_time"],
                            data,
                            successor_data,
                        )
                    )
                elif edge["type"] == "SF":
                    finish = successor_data.get("late_finish")
                    if finish is None:
                        return
                    days = 0 if successor_data["duration"] == 0 else -1
                    if edge["lag_time"]:
                        days += edge["lag_time"]
                    if days:
                        starts.append(
                            datetime.datetime.combine(self.offset_date(finish, -days, data), datetime.time(9))
                        )
                        starts.append(
                            datetime.datetime.combine(
                                self.offset_date(finish, -days, successor_data),
                                datetime.time(9),
                            )
                        )
                    else:
                        starts.append(finish)
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_start"],
                            successor_data["early_finish"],
                            edge["lag_time"],
                            data,
                            successor_data,
                        )
                    )
            if starts and finishes:
                data["late_start"] = min(starts)
                data["late_finish"] = min(finishes)
                if self.offset_date(data["late_start"], data["duration"], data) < data["late_finish"]:
                    data["late_finish"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                        data["late_start"],
                        datetime.timedelta(days=data["duration"]),
                        data["duration_type"],
                        data["calendar"],
                        date_type="FINISH",
                    )
                else:
                    data["late_start"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                        data["late_finish"],
                        datetime.timedelta(days=data["duration"]),
                        data["duration_type"],
                        data["calendar"],
                        date_type="START",
                    )
            elif finishes:
                data["late_finish"] = min(finishes)
            elif starts:
                data["late_start"] = min(starts)
            else:
                print("How did this happen?")

        if data.get("late_finish") is None:
            data["late_finish"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                data["late_start"],
                datetime.timedelta(days=data["duration"]),
                data["duration_type"],
                data["calendar"],
                date_type="FINISH",
            )
        elif data.get("late_start") is None:
            data["late_start"] = ifcopenshell.util.sequence.get_start_or_finish_date(
                data["late_finish"],
                datetime.timedelta(days=data["duration"]),
                data["duration_type"],
                data["calendar"],
                date_type="START",
            )

        if data["duration_type"] == "WORKTIME":
            data["total_float"] = datetime.timedelta(
                days=ifcopenshell.util.sequence.count_working_days(
                    data["early_finish"], data["late_finish"], data["calendar"]
                )
            )
        else:
            data["total_float"] = data["late_finish"] - data["early_finish"]
            # If the float is within the span of a single day, it may show as a 8 hours
            if data["total_float"].seconds == 60 * 60 * 8:
                data["total_float"] = datetime.timedelta(days=data["total_float"].days + 1)

        data["free_float"] = min(free_floats) if free_floats else None
        # If the float is within the span of a single day, it may show as a 8 hours
        if data["free_float"] and data["free_float"].seconds == 60 * 60 * 8:
            data["free_float"] = datetime.timedelta(days=data["free_float"].days + 1)

        return True

    def calculate_free_float(
        self,
        predecessor_date,
        successor_date,
        lag_time,
        predecessor_data,
        successor_data,
    ):
        if not lag_time:
            min_successor_date = successor_date
        else:
            min_successor_date = min(
                (
                    self.offset_date(successor_date, -lag_time, predecessor_data),
                    self.offset_date(successor_date, -lag_time, successor_data),
                )
            )
        if predecessor_data["duration_type"] == "WORKTIME":
            return datetime.timedelta(
                days=ifcopenshell.util.sequence.count_working_days(
                    predecessor_date, min_successor_date, predecessor_data["calendar"]
                )
            )
        return min_successor_date - predecessor_date
