import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"person_and_organisation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["person_and_organisation"]):
            if inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["person_and_organisation"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["person_and_organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcOwnerHistory"):
                self.file.remove(inverse)
        self.file.remove(self.settings["person_and_organisation"])
