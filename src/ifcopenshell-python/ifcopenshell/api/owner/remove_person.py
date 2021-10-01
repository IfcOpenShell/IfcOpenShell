import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"person": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for role in self.settings["person"].Roles or []:
            if len(self.file.get_inverse(role)) == 1:
                ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        for address in self.settings["person"].Addresses or []:
            if len(self.file.get_inverse(address)) == 1:
                ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        for inverse in self.file.get_inverse(self.settings["person"]):
            if inverse.is_a("IfcWorkControl"):
                if inverse.Creators == (self.settings["person"],):
                    inverse.Creators = None
            elif inverse.is_a("IfcInventory"):
                if inverse.ResponsiblePersons == (self.settings["person"],):
                    inverse.ResponsiblePersons = None
            elif inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["person"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcPersonAndOrganization"):
                ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=inverse)
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["person"],):
                    self.file.remove(inverse)
        self.file.remove(self.settings["person"])
