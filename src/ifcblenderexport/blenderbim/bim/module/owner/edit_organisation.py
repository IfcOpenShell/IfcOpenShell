class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "organisation": None,
            "attributes": {}
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["organisation"], name, value)
