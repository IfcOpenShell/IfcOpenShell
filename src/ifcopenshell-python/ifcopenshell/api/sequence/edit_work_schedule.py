import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_schedule": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if value:
                if "Date" in name or "Time" in name:
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
                elif name == "Duration" or name == "TotalFloat":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
            setattr(self.settings["work_schedule"], name, value)
