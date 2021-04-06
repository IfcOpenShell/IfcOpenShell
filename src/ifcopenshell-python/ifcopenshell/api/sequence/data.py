import ifcopenshell.util.date

class Data:
    is_loaded = False
    work_plans = {}
    work_schedules = {}
    tasks = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.work_plans = {}
        cls.work_schedules = {}
        cls.work_calendars = {}
        cls.tasks = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_work_plans()
        cls.load_work_schedules()
        cls.load_work_calendars()
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
    def load_work_schedules(cls):
        cls.work_schedules = {}
        for work_schedule in cls._file.by_type("IfcWorkSchedule"):
            data = work_schedule.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"]).isoformat()
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"]).isoformat()
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"]).isoformat()
            cls.work_schedules[work_schedule.id()] = data

    @classmethod
    def load_work_calendars(cls):
        for work_calendar in cls._file.by_type("IfcWorkCalendar"):
            data = work_calendar.get_info()
            del data["OwnerHistory"]     
            ##### HOW DO WE NEST ENTITIES SUCH AS WORKTIME? ####       
            ##### HOW TO ALLOW DISPLAY OF TIME? AND DATES? ####   
            del data["WorkingTimes"]
            del data["ExceptionTimes"]
            # if data["WorkingTimes"]:
            #     for worktime in data["WorkingTimes"]:
            #         worktime_data = {}
            #         if worktime.Start:                   
            #             worktime_data["start"] = ifcopenshell.util.date.ifc2datetime(worktime.Start).isoformat()
            #         if worktime.Start:
            #             worktime_data["finish"] = ifcopenshell.util.date.ifc2datetime(worktime.Start).isoformat()
            #         worktime = worktime_data
            # if data["ExceptionTimes"]:
            #     for exceptiontime in data["ExceptionTimes"]:
            #         exceptiontime_data = {}
            #         exceptiontime_data["start"] = ifcopenshell.util.date.ifc2datetime(exceptiontime.Finish).isoformat()
            #         exceptiontime_data["finish"] = ifcopenshell.util.date.ifc2datetime(exceptiontime.Finish).isoformat()
            #         exceptiontime = exceptiontime_data
            cls.work_calendars[work_calendar.id()] = data

    @classmethod
    def load_tasks(cls):
        cls.tasks = {}
        for task in cls._file.by_type("IfcTask"):
            cls.tasks[task.id()] = {"Name": task.Name, "Identification": task.Identification or ""}
