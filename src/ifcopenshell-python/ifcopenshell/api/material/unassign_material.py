import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                if rel.RelatingMaterial.is_a("IfcMaterialLayerSetUsage") or rel.RelatingMaterial.is_a(
                    "IfcMaterialProfileSetUsage"
                ):
                    self.file.remove(rel.RelatingMaterial)
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    continue
                related_objects = set(rel.RelatedObjects)
                related_objects.remove(self.settings["product"])
                rel.RelatedObjects = list(related_objects)
