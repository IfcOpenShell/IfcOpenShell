class Usecase():
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "constituent": None,
            "attributes": {},
            "material": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["constituent"], name, value)
        self.settings["constituent"].Material = self.settings["material"]
