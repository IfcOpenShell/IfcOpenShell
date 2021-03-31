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
        work_plan = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkPlan",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        work_plan.CreationDate = ifcopenshell.util.date.datetime2ifc(datetime.now(), "IfcDateTime")
        person = ifcopenshell.api.owner.settings.get_person(self.file)
        if person:
            work_plan.Creators = [person]
        work_plan.StartTime = ifcopenshell.util.date.datetime2ifc(self.settings["start_time"], "IfcDateTime")

        context = self.file.by_type("IfcContext")[0]
        if context.Declares:
            rel_declares = context.Declares[0]
            ifcopenshell.api.run("owner.update_owner_history", self.file, element=rel_declares)
        else:
            rel_declares = self.file.create_entity("IfcRelDeclares", **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingContext": context
            })

        related_definitions = list(rel_declares.RelatedDefinitions or [])
        related_definitions.append(work_plan)
        rel_declares.RelatedDefinitions = related_definitions

        return work_plan
