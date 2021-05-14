import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if value and name in ["Start", "Finish"]:
                value = ifcopenshell.util.date.datetime2ifc(value, "IfcDate")
            setattr(self.settings["work_time"], name, value)
