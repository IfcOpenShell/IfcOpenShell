class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.file.by_type("IfcRelFillsElement"):
            if rel.RelatedBuildingElement == self.settings["element"]:
                self.file.remove(rel)
                break
