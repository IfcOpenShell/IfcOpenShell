class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_calendar": None, "type": "WorkingTimes", "name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_time = self.file.create_entity("IfcWorkTime", **{"Name": self.settings["name"]})
        if self.settings["type"] == "WorkingTimes":
            working_times = list(self.settings["work_calendar"].WorkingTimes or [])
            working_times.append(work_time)
            self.settings["work_calendar"].WorkingTimes = working_times
        elif self.settings["type"] == "ExceptionTimes":
            exception_times = list(self.settings["work_calendar"].ExceptionTimes or [])
            exception_times.append(work_time)
            self.settings["work_calendar"].ExceptionTimes = exception_times
        return work_time
