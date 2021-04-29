class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_calendar": None, "time_type": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_time = self.file.create_entity("IfcWorkTime")
        if self.settings["time_type"] == "WorkingTimes":
            working_times = list(self.settings["work_calendar"].WorkingTimes or [])
            working_times.append(work_time)
            self.settings["work_calendar"].WorkingTimes = working_times
        elif self.settings["time_type"] == "ExceptionTimes":
            exception_times = list(self.settings["work_calendar"].ExceptionTimes or [])
            exception_times.append(work_time)
            self.settings["work_calendar"].ExceptionTimes = exception_times
        return work_time
