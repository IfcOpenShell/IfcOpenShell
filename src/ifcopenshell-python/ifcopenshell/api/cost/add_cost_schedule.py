import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"name": None, "predefined_type": "NOTDEFINED", "start_time": datetime.now()}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        cost_schedule = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcCostSchedule",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        cost_schedule.UpdateDate = ifcopenshell.util.date.datetime2ifc(datetime.now(), "IfcDateTime")
        return cost_schedule
