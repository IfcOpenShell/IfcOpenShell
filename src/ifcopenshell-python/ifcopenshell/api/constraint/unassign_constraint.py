import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "constraint": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesConstraint") and rel.RelatingConstraint == self.settings["constraint"]:
                self.file.remove(rel)
