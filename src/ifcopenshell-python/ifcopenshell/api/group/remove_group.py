class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"group": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["group"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["group"])
