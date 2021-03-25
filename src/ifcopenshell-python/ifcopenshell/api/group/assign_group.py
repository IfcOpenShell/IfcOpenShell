import ifcopenshell
import ifcopenshell.api.owner.create_owner_history as create_owner_history
import ifcopenshell.api.owner.update_owner_history as update_owner_history


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "product": None,
            "group": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["group"].IsGroupedBy:
            return self.file.create_entity("IfcRelAssignsToGroup", **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": create_owner_history.Usecase(self.file).execute(),
                "RelatedObjects": [self.settings["product"]],
                "RelatingGroup": self.settings["group"]
            })
        rel = self.settings["group"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)
        update_owner_history.Usecase(self.file, {"element": rel}).execute()
