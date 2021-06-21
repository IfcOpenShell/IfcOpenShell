import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"load_group": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        for inverse in self.file.get_inverse(self.settings["load_group"]):
            if inverse.is_a("IfcRelAssignsToGroup") and len(inverse.RelatedObjects) == 1:
                self.file.remove(inverse)
        self.file.remove(self.settings["load_group"])
