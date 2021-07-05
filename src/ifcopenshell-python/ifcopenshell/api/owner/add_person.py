class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "identification": "HSeldon",
            "family_name": "Seldon",
            "given_name": "Hari",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        data = {"FamilyName": self.settings["family_name"], "GivenName": self.settings["given_name"]}
        if self.file.schema == "IFC2X3":
            data["Id"] = self.settings["identification"]
        else:
            data["Identification"] = self.settings["identification"]
        return self.file.create_entity("IfcPerson", **data)
