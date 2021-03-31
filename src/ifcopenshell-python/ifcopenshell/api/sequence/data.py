import ifcopenshell.util.date


class Data:
    is_loaded = False
    work_plans = {}
    tasks = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.work_plans = {}
        cls.tasks = {}

    @classmethod
    def load(cls, file):
        cls.work_plans = {}
        cls.tasks = {}
        for work_plan in file.by_type("IfcWorkPlan"):
            data = work_plan.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"])
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"])
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"])
            cls.work_plans[work_plan.id()] = data
        for task in file.by_type("IfcTask"):
            cls.tasks[task.id()] = {"Name": task.Name, "Identification": task.Identification or ""}
        cls.is_loaded=True
