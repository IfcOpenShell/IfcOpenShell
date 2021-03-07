import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"constituent_set": None, "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        constituents = list(self.settings["constituent_set"].MaterialConstituents or [])
        constituent = self.file.create_entity("IfcMaterialConstituent", **{"Material": self.settings["material"]})
        constituents.append(constituent)
        self.settings["constituent_set"].MaterialConstituents = constituents
        return constituent
