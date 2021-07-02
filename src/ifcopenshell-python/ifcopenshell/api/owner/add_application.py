class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"attributes": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcApplication", **self.settings["attributes"])
