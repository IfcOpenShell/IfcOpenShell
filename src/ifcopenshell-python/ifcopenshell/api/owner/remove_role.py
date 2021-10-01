class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"role": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["role"]):
            if inverse.is_a() in ("IfcOrganization", "IfcPerson", "IfcPersonAndOrganization"):
                if inverse.Roles == (self.settings["role"],):
                    inverse.Roles = None
            elif inverse.is_a("IfcResourceLevelRelationship") and not inverse.is_a("IfcOrganizationRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["organisation"],):
                    self.file.remove(inverse)
        self.file.remove(self.settings["role"])
