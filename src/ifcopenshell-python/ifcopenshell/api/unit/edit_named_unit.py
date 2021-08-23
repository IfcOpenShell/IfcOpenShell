class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "Dimensions":
                dimensions = self.settings["unit"].Dimensions
                if len(self.file.get_inverse(dimensions)) > 1:
                    self.settings["unit"].Dimensions = self.file.createIfcDimensionalExponents(*value)
                else:
                    for i, exponent in enumerate(value):
                        dimensions[i] = exponent
                continue
            setattr(self.settings["unit"], name, value)
