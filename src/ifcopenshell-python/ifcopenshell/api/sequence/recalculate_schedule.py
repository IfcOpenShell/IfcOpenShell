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
        import time

        self.time = time.time()
        self.build_network_graph()
        print("{} :: {:.2f}".format("Build network", time.time() - self.time))
        print("TOTAL NODES AND EDGES", len(self.g.nodes), len(self.g.edges))
        self.time = time.time()
        self.calculate_all_paths_sorted_by_duration()
        print("{} :: {:.2f}".format("Calc all paths", time.time() - self.time))
        self.time = time.time()
        self.calculate_critical_path()
        print("{} :: {:.2f}".format("Calc critical", time.time() - self.time))
        self.time = time.time()
        self.calculate_forward_pass()
        print("{} :: {:.2f}".format("Forward", time.time() - self.time))
        self.time = time.time()
        self.calculate_backward_pass()
        print("{} :: {:.2f}".format("Backward", time.time() - self.time))
        self.time = time.time()
        self.update_task_times()
        print("{} :: {:.2f}".format("Update", time.time() - self.time))
        self.time = time.time()
        print("DONE!", self.critical_paths)

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
        # This is less correct, but less computation
        if not task.IsSuccessorFrom:
            self.edges.append(("start", task.id(), {"lag_time": 0, "type": "FS"}))
        # This I think is more correct, but unlikely to be necessary in most
        # graphs, and simply adds more computation time
        # if not predecessor_types or (
        #    "FINISH_START" not in predecessor_types and "START_START" not in predecessor_types
        # ):
        #    self.edges.append(("start", task.id(), {"lag_time": 0, "type": "FS"}))
        if not successor_types or ("FINISH_START" not in successor_types and "FINISH_FINISH" not in successor_types):
            self.edges.append((task.id(), "finish", {"lag_time": 0, "type": "FS"}))

    def calculate_all_paths_sorted_by_duration(self):
        self.paths = []
        total_paths = 0
        for path in nx.algorithms.simple_paths.all_simple_paths(self.g, "start", "finish"):
            total_duration = 0
            for i, node in enumerate(path):
                try:
                    next_edge = self.g[node][path[i + 1]]
                    prev_edge = self.g[path[i - 1]][node]
                except:
                    continue
                if prev_edge["type"][1] == "S" and next_edge["type"][0] == "F":
                    total_duration += self.g.nodes[node]["duration"]
                elif prev_edge["type"][1] == "F" and next_edge["type"][0] == "S":
                    total_duration -= self.g.nodes[node]["duration"]
                total_duration += next_edge["lag_time"]
            self.paths.append((total_duration, path))
            total_paths += 1
            if total_paths % 2000 == 0:
                print(total_paths, total_duration)
        self.paths = list(reversed(sorted(self.paths, key=lambda x: x[0])))

    def calculate_critical_path(self):
        self.critical_paths = [p for p in self.paths if p[0] == self.paths[0][0]]

    def calculate_forward_pass(self):
        for path_data in self.paths:
            path = path_data[1]
            for i, node in enumerate(path):
                data = self.g.nodes[node]

                if node == "start":
                    data["early_start"] = 0
                else:
                    prev_node = self.g.nodes[path[i - 1]]
                    prev_edge = self.g[path[i - 1]][node]
                    if prev_edge["type"] == "FS" and data.get("early_start") is None:
                        data["early_start"] = prev_node["early_finish"] + prev_edge["lag_time"]
                    elif prev_edge["type"] == "FF" and data.get("early_finish") is None:
                        data["early_finish"] = prev_node["early_finish"] + prev_edge["lag_time"]
                    elif prev_edge["type"] == "SS" and data.get("early_start") is None:
                        data["early_start"] = prev_node["early_start"] + prev_edge["lag_time"]
                    elif prev_edge["type"] == "SF" and data.get("early_finish") is None:
                        data["early_finish"] = prev_node["early_start"] + prev_edge["lag_time"]

                if data.get("early_finish") is None:
                    data["early_finish"] = data["early_start"] + data["duration"]
                elif data.get("early_start") is None:
                    data["early_start"] = data["early_finish"] - data["duration"]
                #print(data)

    def calculate_backward_pass(self):
        critical_duration = self.critical_paths[0][0]
        for path_data in self.paths:
            path = list(reversed(path_data[1]))
            for i, node in enumerate(path):
                data = self.g.nodes[node]

                if node == "finish":
                    data["late_finish"] = critical_duration
                else:
                    prev_node = self.g.nodes[path[i - 1]]
                    prev_edge = self.g[node][path[i - 1]]
                    if prev_edge["type"] == "FS" and data.get("late_finish") is None:
                        data["late_finish"] = prev_node["late_start"] - prev_edge["lag_time"]
                    elif prev_edge["type"] == "FF" and data.get("late_finish") is None:
                        data["late_finish"] = prev_node["late_finish"] - prev_edge["lag_time"]
                    elif prev_edge["type"] == "SS" and data.get("late_start") is None:
                        data["late_start"] = prev_node["late_start"] - prev_edge["lag_time"]
                    elif prev_edge["type"] == "SF" and data.get("late_start") is None:
                        data["late_start"] = prev_node["late_finish"] - prev_edge["lag_time"]

                if data.get("late_finish") is None:
                    data["late_finish"] = data["late_start"] + data["duration"]
                elif data.get("late_start") is None:
                    data["late_start"] = data["late_finish"] - data["duration"]

                data["total_float"] = data["late_finish"] - data["early_finish"]
                #print("DATA", data)

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
