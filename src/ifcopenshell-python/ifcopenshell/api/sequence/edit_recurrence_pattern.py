import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"recurrence_pattern": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "TimePeriods" and value:
                periods = []
                for period in value:
                    periods.append(self.file.create_entity("IfcTimePeriod", **{
                        "StartTime": ifcopenshell.util.date.datetime2ifc(period[0]),
                        "EndTime": ifcopenshell.util.date.datetime2ifc(period[1])
                    }))
                value = periods
            setattr(self.settings["recurrence_pattern"], name, value)
