class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "Identification": "HSeldon",
            "FamilyName": "Seldon",
            "GivenName": "Hari",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcPerson", **self.settings)
