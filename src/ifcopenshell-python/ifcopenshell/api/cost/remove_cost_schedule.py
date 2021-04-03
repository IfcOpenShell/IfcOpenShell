class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_schedule": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        self.file.remove(self.settings["cost_schedule"])
