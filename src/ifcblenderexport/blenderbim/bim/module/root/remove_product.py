class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["product"])
