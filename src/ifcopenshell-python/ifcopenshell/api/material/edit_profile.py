class Usecase():
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "profile": None,
            "attributes": {},
            "profile_attributes": {},
            "material": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["profile"], name, value)
        self.settings["profile"].Material = self.settings["material"]
        for name, value in self.settings["profile_attributes"].items():
            setattr(self.settings["profile"].Profile, name, value)
