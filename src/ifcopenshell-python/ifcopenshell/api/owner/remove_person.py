class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"person": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["person"])
