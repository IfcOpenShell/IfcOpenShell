class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"resource": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        self.file.remove(self.settings["resource"])
