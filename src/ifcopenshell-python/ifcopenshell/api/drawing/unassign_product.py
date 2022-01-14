import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_product": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["related_object"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToProduct") or rel.RelatingProduct != self.settings["relating_product"]:
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel
