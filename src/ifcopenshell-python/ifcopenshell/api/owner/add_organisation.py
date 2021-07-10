class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "identification": "APTR",
            "name": "Aperture Science",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        data = {"Name": self.settings["name"]}
        if self.file.schema == "IFC2X3":
            data["Id"] = self.settings["identification"]
        else:
            data["Identification"] = self.settings["identification"]
        return self.file.create_entity("IfcOrganization", **data)
