import ifcopenshell.util.date


class Data:
    is_loaded = False
    work_plans = {}
    work_schedules = {}
    tasks = {}
    task_times = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.work_plans = {}
        cls.work_schedules = {}
        cls.work_calendars = {}
        cls.tasks = {}
        cls.task_times = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_work_plans()
        cls.load_work_schedules()
        cls.load_work_calendars()
        cls.load_tasks()
        cls.load_task_times()
        cls.is_loaded = True

    @classmethod
    def load_work_plans(cls):
        cls.work_plans = {}
        for work_plan in cls._file.by_type("IfcWorkPlan"):
            data = work_plan.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"])
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"])
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"])
            data["IsDecomposedBy"] = []
            for rel in work_plan.IsDecomposedBy:
                data["IsDecomposedBy"].extend([o.id() for o in rel.RelatedObjects])
            cls.work_plans[work_plan.id()] = data

    @classmethod
    def load_work_schedules(cls):
        cls.work_schedules = {}
        for work_schedule in cls._file.by_type("IfcWorkSchedule"):
            data = work_schedule.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"])
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"])
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"])
            data["RelatedObjects"] = []
            for rel in work_schedule.Controls:
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcTask"):
                        data["RelatedObjects"].append(obj.id())
            cls.work_schedules[work_schedule.id()] = data

    @classmethod
    def load_work_calendars(cls):
        cls.work_calendars = {}
        for work_calendar in cls._file.by_type("IfcWorkCalendar"):
            data = work_calendar.get_info()
            del data["OwnerHistory"]
            del data["WorkingTimes"]
            del data["ExceptionTimes"]
            cls.work_calendars[work_calendar.id()] = data

    @classmethod
    def load_tasks(cls):
        cls.tasks = {}
        for task in cls._file.by_type("IfcTask"):
            data = task.get_info()
            del data["OwnerHistory"]
            data["RelatedObjects"] = []
            data["RelatingProducts"] = []
            data["IsPredecessorTo"] = []
            data["IsSuccessorFrom"] = []
            if task.TaskTime:
                data["TaskTime"] = data["TaskTime"].id()
            for rel in task.IsNestedBy:
                [data["RelatedObjects"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcTask")]
            [
                data["RelatingProducts"].append(r.RelatingProduct.id())
                for r in task.HasAssignments
                if r.is_a("IfcRelAssignsToProduct")
            ]
            [data["IsPredecessorTo"].append(rel.RelatedProcess.id()) for rel in task.IsPredecessorTo or []]
            [data["IsSuccessorFrom"].append(rel.RelatingProcess.id()) for rel in task.IsSuccessorFrom or []]
            cls.tasks[task.id()] = data

    @classmethod
    def load_task_times(cls):
        cls.task_times = {}
        for task_time in cls._file.by_type("IfcTaskTime"):
            data = task_time.get_info()
            for key, value in data.items():
                if not value:
                    continue
                if "Start" in key or "Finish" in key or key == "StatusTime":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
                # TODO parse duration
            cls.task_times[task_time.id()] = data
