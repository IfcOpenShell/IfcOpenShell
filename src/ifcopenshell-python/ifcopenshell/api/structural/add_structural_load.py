import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": None,
            "ifc_class": "IfcStructuralLoadLinearForce",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity(self.settings["ifc_class"], Name=self.settings["name"])
