import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "task": None,
            "sequence_type":"FINISH_START",
            "successor_task": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        #TODO: tasks can only have one relationship between oneanother: if a relationship is already assigned, it should overide the previous one's settings.
        rel_sequence = self.file.create_entity("IfcRelSequence",**{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingProcess": self.settings["task"],
                "SequenceType": self.settings["sequence_type"],
                "RelatedProcess": self.settings["successor_task"],
            })
        return rel_sequence