import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "library": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.createIfcLibraryReference(ReferencedLibrary=self.settings["library"])
