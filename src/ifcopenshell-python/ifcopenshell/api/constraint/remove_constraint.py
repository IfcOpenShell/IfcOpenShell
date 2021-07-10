class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"constraint": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["constraint"])
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if not rel.RelatingConstraint:
                self.file.remove(rel)
