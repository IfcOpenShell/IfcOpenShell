class Usecase():
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "layer": None,
            "attributes": {},
            "material": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["layer"], name, value)
        self.settings["layer"].Material = self.settings["material"]
