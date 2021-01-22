class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"document": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["document"])
        for rel in self.file.by_type("IfcRelAssociatesDocument"):
            if not rel.RelatingDocument:
                self.file.remove(rel)
