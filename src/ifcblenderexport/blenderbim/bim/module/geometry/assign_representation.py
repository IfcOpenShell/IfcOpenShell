class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "representation": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        definition = self.settings["product"].Representation
        if not definition:
            definition = self.file.createIfcProductDefinitionShape()
        representations = list(definition.Representations)
        representations.append(self.settings["representation"])
        definition.Representations = representations
