import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"task": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["task"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        self.file.remove(self.settings["task"])
