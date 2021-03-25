class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "Identification": "APTR",
            "Name": "Aperture Science",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcOrganization", **self.settings)
