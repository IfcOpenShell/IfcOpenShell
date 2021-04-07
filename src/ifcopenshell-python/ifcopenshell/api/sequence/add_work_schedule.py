import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": "Unnamed",
            "predefined_type": "NOTDEFINED",
            "start_time": datetime.now(),
            "work_plan": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_schedule = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkSchedule",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        work_schedule.CreationDate = ifcopenshell.util.date.datetime2ifc(datetime.now(), "IfcDateTime")
        person = ifcopenshell.api.owner.settings.get_person(self.file)
        if person:
            work_schedule.Creators = [person]
        work_schedule.StartTime = ifcopenshell.util.date.datetime2ifc(self.settings["start_time"], "IfcDateTime")

        if self.settings["work_plan"]:
            ifcopenshell.api.run(
                "aggregate.assign_object",
                self.file,
                **{"product": work_schedule, "relating_object": self.settings["work_plan"]}
            )
        else:
            # TODO: this is an ambiguity by buildingSMART
            # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration", self.file, definition=work_schedule, relating_context=context
            )
        return work_schedule
