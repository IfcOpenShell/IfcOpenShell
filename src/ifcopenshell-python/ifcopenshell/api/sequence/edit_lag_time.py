class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"rel_sequence": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "LagValue" and value is not None:
                # TODO: support RatioMeasure
                value = self.file.createIfcDuration(value)
            setattr(self.settings["rel_sequence"], name, value)
