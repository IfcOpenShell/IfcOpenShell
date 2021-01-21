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
            self.settings["product"].Representation = definition
        representations = list(definition.Representations) if definition.Representations else []
        representations.append(self.settings["representation"])
        definition.Representations = representations
