import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "definition": None,
            "relating_context": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["definition"].HasContext:
            return
        rel = self.settings["definition"].HasContext[0]
        related_definitions = set(rel.RelatedDefinitions) or set()
        related_definitions.remove(self.settings["definition"])
        if len(related_definitions):
            rel.RelatedDefinitions = list(related_definitions)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        else:
            self.file.remove(rel)
