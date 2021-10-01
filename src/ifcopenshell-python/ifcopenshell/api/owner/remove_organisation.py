import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"organisation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for role in self.settings["organisation"].Roles or []:
            if len(self.file.get_inverse(role)) == 1:
                ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        for address in self.settings["organisation"].Addresses or []:
            if len(self.file.get_inverse(address)) == 1:
                ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        for inverse in self.file.get_inverse(self.settings["organisation"]):
            if inverse.is_a("IfcOrganizationRelationship"):
                if inverse.RelatingOrganization == self.settings["organisation"]:
                    self.file.remove(inverse)
                elif inverse.RelatedOrganizations == (self.settings["organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["organisation"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcPersonAndOrganization"):
                ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=inverse)
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship") and not inverse.is_a("IfcOrganizationRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcApplication"):
                ifcopenshell.api.run("owner.remove_application", self.file, application=inverse)

        self.file.remove(self.settings["organisation"])
