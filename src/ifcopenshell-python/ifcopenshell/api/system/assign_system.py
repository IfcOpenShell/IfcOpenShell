import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "system": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["system"].IsGroupedBy:
            return self.file.create_entity(
                "IfcRelAssignsToGroup",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingGroup": self.settings["system"],
                }
            )
        rel = self.settings["system"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)
        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
