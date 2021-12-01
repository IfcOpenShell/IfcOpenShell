class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"metric": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.remove(self.settings["metric"])
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if not rel.RelatingConstraint:
                self.file.remove(rel)
        for resource_rel in self.file.by_type("IfcResourceConstraintRelationship"):
            if not resource_rel.RelatingConstraint:
                self.file.remove(resource_rel)
