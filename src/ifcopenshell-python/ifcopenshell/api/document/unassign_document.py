import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "document": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument == self.settings["document"]:
                self.file.remove(rel)
