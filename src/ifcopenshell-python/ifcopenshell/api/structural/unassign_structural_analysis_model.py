import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "structural_analysis_model": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["structural_analysis_model"].IsGroupedBy:
            return
        rel = self.settings["structural_analysis_model"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.remove(self.settings["product"])
        if len(related_objects):
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        else:
            self.file.remove(rel)
