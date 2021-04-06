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
        cls._file = file
        if not cls._file:
            return
        cls.load_work_plans()
        cls.load_work_schedules()
        cls.load_tasks()
        cls.is_loaded=True

    @classmethod
    def load_work_plans(cls):
        cls.work_plans = {}
        for work_plan in cls._file.by_type("IfcWorkPlan"):
            data = work_plan.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"]).isoformat()
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"]).isoformat()
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"]).isoformat()
            cls.work_plans[work_plan.id()] = data

    @classmethod
    def load_tasks(cls):
        cls.tasks = {}
        for task in cls._file.by_type("IfcTask"):
            cls.tasks[task.id()] = {"Name": task.Name, "Identification": task.Identification or ""}
