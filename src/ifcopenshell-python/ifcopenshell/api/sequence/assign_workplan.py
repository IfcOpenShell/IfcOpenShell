import ifcopenshell
import ifcopenshell.api

class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "work_schedule": None,
            "work_plan":None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        ###Project declaration should be removed if the workschedule is assigned to a project.####
        if self.settings["work_schedule"].HasContext:
            rel_declares = self.settings["work_schedule"].HasContext[0]
            related_definitions = list(rel_declares.RelatedDefinitions)
            related_definitions.remove(self.settings["work_schedule"])
            rel_declares.RelatedDefinitions = related_definitions
        if self.settings["work_plan"].IsDecomposedBy:
            rel_aggregates = self.settings["work_plan"].IsDecomposedBy[0]
            related_objects = list(rel_aggregates.RelatedObjects or [])
            related_objects.append(self.settings["work_schedule"])
            rel_aggregates.RelatedObjects = related_objects
        else:             
            rel_aggregates = ifcopenshell.api.run("aggregate.assign_object", self.file, **{
                "product": self.settings["work_schedule"],
                "relating_object": self.settings["work_plan"]
            })
        return rel_aggregates