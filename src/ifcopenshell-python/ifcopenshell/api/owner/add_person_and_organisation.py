class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"person": None, "organisation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.createIfcPersonAndOrganization(self.settings["person"], self.settings["organisation"])
