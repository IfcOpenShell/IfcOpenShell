import datetime
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"resource_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.resource = self.get_resource()

        # If the user specifies both an end date and a duration, the duration takes priority
        if (
            self.settings["attributes"].get("ScheduleWork", None)
            and "ScheduleFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ScheduleFinish"]
        if self.settings["attributes"].get("ActualWork", None) and "ActualFinish" in self.settings["attributes"].keys():
            del self.settings["attributes"]["ActualFinish"]

        for name, value in self.settings["attributes"].items():
            if value:
                if "Start" in name or "Finish" in name or name == "StatusTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
                elif name == "ScheduleWork" or name == "ActualWork" or name == "RemainingTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
            setattr(self.settings["resource_time"], name, value)

    def get_resource(self):
        return [e for e in self.file.get_inverse(self.settings["resource_time"]) if e.is_a("IfcResource")][0]
