class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"layer": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["layer"])
