import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcLibraryInformation", Name=self.settings["name"])
