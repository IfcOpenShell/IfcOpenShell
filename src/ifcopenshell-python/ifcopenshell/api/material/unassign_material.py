import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for association in self.settings["product"].HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                self.file.remove(association)
