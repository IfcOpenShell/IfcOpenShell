import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"rel_sequence": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["rel_sequence"], name, value)
        if "SequenceType" in self.settings["attributes"].keys():
            ifcopenshell.api.run(
                "sequence.cascade_schedule", self.file, task=self.settings["rel_sequence"].RelatedProcess
            )
