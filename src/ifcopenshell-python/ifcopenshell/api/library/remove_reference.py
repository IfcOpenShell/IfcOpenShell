class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"reference": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["reference"].LibraryRefForObjects:
            self.file.remove(rel)
        self.file.remove(self.settings["reference"])
