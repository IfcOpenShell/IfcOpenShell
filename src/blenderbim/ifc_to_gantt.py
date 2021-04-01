import json
import ifcopenshell

class IfcToGantt:
    def __init__(self):
        self.json = []

    def execute(self):
        self.file = ifcopenshell.open("p6.ifc")
        self.root = self.file.by_type("IfcTask")[0]
        task = self.root
        for task in self.file.by_type("IfcTask"):
            self.json.append({
                "pID": task.id(),
                "pName": task.Name,
                "pStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
                "pEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
                "pPlanStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
                "pPlanEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
                "pClass": "ggroupblack",
                "pMile": 1 if task.IsMilestone else 0,
                "pComp": 0,
                "pGroup": 1,
                "pParent": task.Nests[0].RelatingObject.id() if task.Nests else 0,
                "pOpen": 1,
                "pCost":  1
            })
        with open("p6.json", "w") as f:
            json.dump(self.json, f)

ifc_to_gantt = IfcToGantt()
ifc_to_gantt.execute()

