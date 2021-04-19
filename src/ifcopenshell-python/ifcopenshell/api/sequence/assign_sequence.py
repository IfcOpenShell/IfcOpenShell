import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_process": None,
            "related_process": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["related_process"].IsSuccessorFrom or []:
            if rel.RelatingProcess == self.settings["relating_process"]:
                return rel
        return self.file.create_entity(
            "IfcRelSequence",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingProcess": self.settings["relating_process"],
                "RelatedProcess": self.settings["related_process"],
            }
        )
