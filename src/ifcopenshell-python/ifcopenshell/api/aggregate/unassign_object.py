import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_object": None,
            "product": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["product"].Decomposes or []:
            if not rel.is_a("IfcRelAggregates") or rel.RelatingObject != self.settings["relating_object"]:
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["product"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel
