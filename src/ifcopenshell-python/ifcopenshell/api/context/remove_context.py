class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"context": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: this is a light remove only
        for subcontext in self.settings["context"].HasSubContexts:
            self.file.remove(subcontext)
        self.file.remove(self.settings["context"])
