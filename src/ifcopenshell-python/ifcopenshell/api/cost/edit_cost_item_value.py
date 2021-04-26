class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_value": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "AppliedValue" and value is not None:
                # TODO: support all applied value select types
                value = self.file.createIfcReal(value)
            setattr(self.settings["cost_value"], name, value)
