import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "constraint": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        rel = self.get_constraint_rel()
        related_objects = set(rel.RelatedObjects) if rel.RelatedObjects else set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)

    def get_constraint_rel(self):
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if rel.RelatingConstraint == self.settings["constraint"]:
                return rel
        return self.file.create_entity("IfcRelAssociatesConstraint", **{
            "GlobalId": ifcopenshell.guid.new(),
            # TODO: owner history
            "RelatingConstraint": self.settings["constraint"]
        })
