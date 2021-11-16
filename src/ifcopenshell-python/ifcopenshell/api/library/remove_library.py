class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"library": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for reference in set(self.settings["library"].HasLibraryReferences or []):
            self.file.remove(reference)
        self.file.remove(self.settings["library"])
        for rel in self.file.by_type("IfcRelAssociatesLibrary"):
            if not rel.RelatingLibrary:
                self.file.remove(rel)
