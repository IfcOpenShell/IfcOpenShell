import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_schedule": None, "work_plan": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: this is an ambiguity by buildingSMART
        # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["work_schedule"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        rel_aggregates = ifcopenshell.api.run(
            "aggregate.assign_object",
            self.file,
            **{"product": self.settings["work_schedule"], "relating_object": self.settings["work_plan"]}
        )
        return rel_aggregates
