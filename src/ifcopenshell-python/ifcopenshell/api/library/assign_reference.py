import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "reference": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.schema == "IFC2X3":
            rels = self.get_ifc2x3_rels()
        else:
            rels = self.settings["reference"].LibraryRefForObjects
        if not rels:
            return self.file.create_entity(
                "IfcRelAssociatesLibrary",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
                RelatedObjects=[self.settings["product"]],
                RelatingLibrary=self.settings["reference"],
            )

        for rel in rels:
            if self.settings["product"] in rel.RelatedObjects:
                return rel

        rel = rels[0]
        related_objects = list(rel.RelatedObjects)
        related_objects.append(self.settings["product"])
        rel.RelatedObjects = related_objects
        ifcopenshell.api.run("owner.update_owner_history", self.file, element=rel)
        return rel

    def get_ifc2x3_rels(self):
        return [
            r for r in self.file.by_type("IfcRelAssociatesLibrary") if r.RelatingLibrary == self.settings["reference"]
        ]
