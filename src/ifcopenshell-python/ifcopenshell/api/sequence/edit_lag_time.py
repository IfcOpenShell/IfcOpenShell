import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"lag_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "LagValue" and value is not None:
                if isinstance(value, float):
                    value = self.file.createIfcRatioMeasure(value)
                else:
                    value = self.file.createIfcDuration(ifcopenshell.util.date.datetime2ifc(value, "IfcDuration"))
            setattr(self.settings["lag_time"], name, value)
