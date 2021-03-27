import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        inverse_elements = self.file.get_inverse(self.settings["material"])
        self.file.remove(self.settings["material"])
        # TODO: this is probably not robust enough
        for inverse in inverse_elements:
            if inverse.is_a("IfcMaterialConstituent"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialLayer"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialProfile"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssociatesMaterial"):
                self.file.remove(inverse)
