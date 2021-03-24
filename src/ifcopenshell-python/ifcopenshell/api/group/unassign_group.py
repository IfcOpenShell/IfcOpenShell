import ifcopenshell
from ifcopenshell.api.owner.api import update_owner_history


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
            return
        rel = self.settings["group"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.remove(self.settings["product"])
        if len(related_objects):
            rel.RelatedObjects = list(related_objects)
            update_owner_history(rel)
        else:
            self.file.remove(rel)
