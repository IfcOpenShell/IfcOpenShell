import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"task_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if "Start" in name or "Finish" in name or name == "StatusTime":
                if value:
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
            setattr(self.settings["task_time"], name, value)
