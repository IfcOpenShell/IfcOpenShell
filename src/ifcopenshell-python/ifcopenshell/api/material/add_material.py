import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"Name": "Unnamed"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcMaterial", **{"Name": self.settings["Name"] or "Unnamed"})
