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
        if self.file.schema == "IFC2X3":
            reference = self.file.createIfcLibraryReference()
            references = list(self.settings["library"].LibraryReference or [])
            references.append(reference)
            self.settings["library"].LibraryReference = references
            return reference
        return self.file.createIfcLibraryReference(ReferencedLibrary=self.settings["library"])
