import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_schedule": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["work_schedule"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        for rel in self.settings["work_schedule"].Controls:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTask"):
                    ifcopenshell.api.run("sequence.remove_task", self.file, task=related_object)
        self.file.remove(self.settings["work_schedule"])
