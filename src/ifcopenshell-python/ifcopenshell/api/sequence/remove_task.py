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
        for inverse in self.file.get_inverse(self.settings["task"]):
            if inverse.is_a("IfcRelSequence"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["task"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run("sequence.remove_task", self.file, task=related_object)
                elif inverse.RelatedObjects == tuple(self.settings["task"]):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                self.file.remove(inverse)
        self.file.remove(self.settings["task"])
