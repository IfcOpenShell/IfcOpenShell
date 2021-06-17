import datetime
import networkx as nx
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.sequence


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_schedule": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # The method implemented is the same as shown here:
        # https://www.youtube.com/watch?v=qTErIV6OqLg
        self.start_dates = []
        self.build_network_graph()

        self.pending_nodes = set(self.g.nodes)
        while self.pending_nodes:
            remaining_nodes = set()
            for pending_node in self.pending_nodes:
                if not self.forward_pass(pending_node):
                    remaining_nodes.add(pending_node)
            self.pending_nodes = remaining_nodes

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
                    rel.RelatedProcess.id(),
                    {
                        "lag_time": 0
                        if not rel.TimeLag
                        else ifcopenshell.util.date.ifc2datetime(rel.TimeLag.LagValue.wrappedValue).days,
                        "type": self.sequence_type_map[rel.SequenceType],
                    },
                )
                for rel in task.IsSuccessorFrom or []
            ]
        )
        predecessor_types = [rel.SequenceType for rel in task.IsSuccessorFrom]
        successor_types = [rel.SequenceType for rel in task.IsPredecessorTo]

        if not predecessor_types or (
            "FINISH_START" not in predecessor_types and "START_START" not in predecessor_types
        ):
            self.edges.append(("start", task.id(), {"lag_time": 0, "type": "FS"}))
            if task.TaskTime and task.TaskTime.ScheduleStart:
                self.start_dates.append(ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleStart))
        if not successor_types or ("FINISH_START" not in successor_types and "FINISH_FINISH" not in successor_types):
            self.edges.append((task.id(), "finish", {"lag_time": 0, "type": "FS"}))

    def update_task_times(self):
        for ifc_definition_id in self.g.nodes:
            data = self.g.nodes[ifc_definition_id]
            if not data["duration"]:
                continue
            ifcopenshell.api.run(
                "sequence.edit_task_time",
                self.file,
                task_time=self.file.by_id(ifc_definition_id).TaskTime,
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
        return ifcopenshell.util.sequence.get_finish_date(
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
            for predecessor in predecessors:
                predecessor_data = self.g.nodes[predecessor]
                edge = self.g[predecessor][node]
                if edge["type"] == "FS":
                    finish = predecessor_data.get("early_finish")
                    if finish is None:
                        return
                    if not edge["lag_time"]:
                        starts.append(finish)
                    else:
                        starts.append(self.offset_date(finish, edge["lag_time"], data))
                        starts.append(self.offset_date(finish, edge["lag_time"], predecessor_data))
                elif edge["type"] == "SS":
                    start = predecessor_data.get("early_start")
                    if start is None:
                        return
                    if not edge["lag_time"]:
                        starts.append(start)
                    else:
                        starts.append(self.offset_date(start, edge["lag_time"], data))
                        starts.append(self.offset_date(start, edge["lag_time"], predecessor_data))
                elif edge["type"] == "FF":
                    finish = predecessor_data.get("early_finish")
                    if finish is None:
                        return
                    if not edge["lag_time"]:
                        finishes.append(finish)
                    else:
                        finishes.append(self.offset_date(finish, edge["lag_time"], data))
                        finishes.append(self.offset_date(finish, edge["lag_time"], predecessor_data))
                elif edge["type"] == "SF":
                    start = predecessor_data.get("early_start")
                    if start is None:
                        return
                    if not edge["lag_time"]:
                        finishes.append(start)
                    else:
                        finishes.append(self.offset_date(start, edge["lag_time"], data))
                        finishes.append(self.offset_date(start, edge["lag_time"], predecessor_data))
            if starts and finishes:
                data["early_start"] = max(starts)
                data["early_finish"] = max(finishes)
                if self.offset_date(data["early_start"], data["duration"], data) > data["early_finish"]:
                    data["early_finish"] = self.offset_date(data["early_start"], data["duration"], data)
                else:
                    data["early_start"] = self.offset_date(data["early_finish"], -data["duration"], data)
            elif finishes:
                data["early_finish"] = max(finishes)
            elif starts:
                data["early_start"] = max(starts)
            else:
                print("How did this happen?")

        if data.get("early_finish") is None:
            data["early_finish"] = self.offset_date(data["early_start"], data["duration"], data)
        elif data.get("early_start") is None:
            data["early_start"] = self.offset_date(data["early_finish"], -data["duration"], data)

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
                    if not edge["lag_time"]:
                        finishes.append(start)
                    else:
                        finishes.append(self.offset_date(start, -edge["lag_time"], data))
                        finishes.append(self.offset_date(start, -edge["lag_time"], successor_data))
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_finish"], successor_data["early_start"], edge["lag_time"], data, successor_data
                        )
                    )
                elif edge["type"] == "SS":
                    start = successor_data.get("late_start")
                    if start is None:
                        return
                    if not edge["lag_time"]:
                        starts.append(start)
                    else:
                        starts.append(self.offset_date(start, -edge["lag_time"], data))
                        starts.append(self.offset_date(start, -edge["lag_time"], successor_data))
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_start"], successor_data["early_start"], edge["lag_time"], data, successor_data
                        )
                    )
                elif edge["type"] == "FF":
                    finish = successor_data.get("late_finish")
                    if finish is None:
                        return
                    if not edge["lag_time"]:
                        finishes.append(finish)
                    else:
                        finishes.append(self.offset_date(finish, -edge["lag_time"], data))
                        finishes.append(self.offset_date(finish, -edge["lag_time"], successor_data))
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_finish"], successor_data["early_finish"], edge["lag_time"], data, successor_data
                        )
                    )
                elif edge["type"] == "SF":
                    finish = successor_data.get("late_finish")
                    if finish is None:
                        return
                    if not edge["lag_time"]:
                        starts.append(finish)
                    else:
                        starts.append(self.offset_date(finish, -edge["lag_time"], data))
                        starts.append(self.offset_date(finish, -edge["lag_time"], successor_data))
                    free_floats.append(
                        self.calculate_free_float(
                            data["early_start"], successor_data["early_finish"], edge["lag_time"], data, successor_data
                        )
                    )
            if starts and finishes:
                data["late_start"] = min(starts)
                data["late_finish"] = min(finishes)
                if self.offset_date(data["late_start"], data["duration"], data) < data["late_finish"]:
                    data["late_finish"] = self.offset_date(data["late_start"], data["duration"], data)
                else:
                    data["late_start"] = self.offset_date(data["late_finish"], -data["duration"], data)
            elif finishes:
                data["late_finish"] = min(finishes)
            elif starts:
                data["late_start"] = min(starts)
            else:
                print("How did this happen?")

        if data.get("late_finish") is None:
            data["late_finish"] = self.offset_date(data["late_start"], data["duration"], data)
        elif data.get("late_start") is None:
            data["late_start"] = self.offset_date(data["late_finish"], -data["duration"], data)

        if data["duration_type"] == "WORKTIME":
            data["total_float"] = datetime.timedelta(
                days=ifcopenshell.util.sequence.count_working_days(
                    data["early_finish"], data["late_finish"], data["calendar"]
                )
            )
        else:
            data["total_float"] = data["late_finish"] - data["early_finish"]

        data["free_float"] = min(free_floats) if free_floats else None

        return True

    def calculate_free_float(self, predecessor_date, successor_date, lag_time, predecessor_data, successor_data):
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
