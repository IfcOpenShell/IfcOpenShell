import datetime
import networkx as nx
import ifcopenshell.api
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_schedule": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # I learned everything about project dependency calcs from this YouTube playlist:
        # https://www.youtube.com/playlist?list=PLLRADeJk4TCK-X5vJY8focpFkau1MR7do
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

        # TODO: normalise durations to elapsed times. Leave this debug print until we finish this TODO.
        for n in self.g.nodes:
            if n == 'start' or n == 'finish':
                print(n, self.g.nodes[n])
            else:
                print(self.file.by_id(n), self.g.nodes[n])

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
        self.g.add_node("start", duration=0)
        self.g.add_node("finish", duration=0)
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
        else:
            duration = 0
        self.g.add_node(task.id(), duration=duration)
        self.edges.extend(
            [
                (
                    rel.RelatingProcess.id(),
                    rel.RelatedProcess.id(),
                    {
                        "lag_time": 0
                        if not rel.TimeLag or not rel.TimeLag.LagValue
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
                    "TotalFloat": ifcopenshell.util.date.datetime2ifc(
                        datetime.timedelta(days=data["total_float"]), "IfcDuration"
                    ),
                    "IsCritical": data["total_float"] == 0,
                },
            )

    def forward_pass(self, node):
        successors = self.g.successors(node)
        predecessors = list(self.g.predecessors(node))
        data = self.g.nodes[node]

        if node == "start":
            data["early_start"] = 0
        else:
            finishes = []
            starts = []
            for predecessor in predecessors:
                edge = self.g[predecessor][node]
                if edge["type"] == "FS":
                    finish = self.g.nodes[predecessor].get("early_finish")
                    if finish is None:
                        return
                    starts.append(finish + edge["lag_time"])
                elif edge["type"] == "SS":
                    start = self.g.nodes[predecessor].get("early_start")
                    if start is None:
                        return
                    starts.append(start + edge["lag_time"])
                elif edge["type"] == "FF":
                    finish = self.g.nodes[predecessor].get("early_finish")
                    if finish is None:
                        return
                    finishes.append(finish + edge["lag_time"])
                elif edge["type"] == "SF":
                    start = self.g.nodes[predecessor].get("early_start")
                    if start is None:
                        return
                    finishes.append(start + edge["lag_time"])
            if starts and finishes:
                data["early_start"] = max(starts)
                data["early_finish"] = max(finishes)
                if data["early_start"] + data["duration"] > data["early_finish"]:
                    data["early_finish"] = data["early_start"] + data["duration"]
                else:
                    data["early_start"] = data["early_finish"] - data["duration"]
            elif finishes:
                data["early_finish"] = max(finishes)
            elif starts:
                data["early_start"] = max(starts)
            else:
                print("How did this happen?")

        if data.get("early_finish") is None:
            data["early_finish"] = data["early_start"] + data["duration"]
        elif data.get("early_start") is None:
            data["early_start"] = data["early_finish"] - data["duration"]

        return True

    def backward_pass(self, node):
        successors = list(self.g.successors(node))
        predecessors = self.g.predecessors(node)
        data = self.g.nodes[node]

        if node == "finish":
            data["late_finish"] = data["early_finish"]
        else:
            finishes = []
            starts = []
            for successor in successors:
                edge = self.g[node][successor]
                if edge["type"] == "FS":
                    start = self.g.nodes[successor].get("late_start")
                    if start is None:
                        return
                    finishes.append(start - edge["lag_time"])
                elif edge["type"] == "SS":
                    start = self.g.nodes[successor].get("late_start")
                    if start is None:
                        return
                    starts.append(start - edge["lag_time"])
                elif edge["type"] == "FF":
                    finish = self.g.nodes[successor].get("late_finish")
                    if finish is None:
                        return
                    finishes.append(finish - edge["lag_time"])
                elif edge["type"] == "SF":
                    finish = self.g.nodes[successor].get("late_finish")
                    if finish is None:
                        return
                    starts.append(finish - edge["lag_time"])
            if starts and finishes:
                data["late_start"] = min(starts)
                data["late_finish"] = min(finishes)
                if data["late_start"] + data["duration"] < data["late_finish"]:
                    data["late_finish"] = data["late_start"] + data["duration"]
                else:
                    data["late_start"] = data["late_finish"] - data["duration"]
            elif finishes:
                data["late_finish"] = min(finishes)
            elif starts:
                data["late_start"] = min(starts)
            else:
                print("How did this happen?")

        if data.get("late_finish") is None:
            data["late_finish"] = data["late_start"] + data["duration"]
        elif data.get("late_start") is None:
            data["late_start"] = data["late_finish"] - data["duration"]

        data["total_float"] = data["late_finish"] - data["early_finish"]

        return True
