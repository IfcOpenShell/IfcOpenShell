import ifcopenshell.util.date


class Data:
    is_loaded = False
    cost_schedules = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.cost_schedules = {}

    @classmethod
    def load(cls, file):
        cls.cost_schedules = {}
        for cost_schedule in file.by_type("IfcCostSchedule"):
            data = cost_schedule.get_info()
            del data["OwnerHistory"]
            if data["SubmittedOn"]:
                data["SubmittedOn"] = ifcopenshell.util.date.ifc2datetime(data["SubmittedOn"])
            if data["UpdateDate"]:
                data["UpdateDate"] = ifcopenshell.util.date.ifc2datetime(data["UpdateDate"])
            cls.cost_schedules[cost_schedule.id()] = data
        cls.is_loaded=True
