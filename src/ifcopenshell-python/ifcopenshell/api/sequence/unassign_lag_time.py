import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "rel_sequence": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if len(self.file.get_inverse(self.settings["rel_sequence"].TimeLag)) == 1:
            self.file.remove(self.settings["rel_sequence"].TimeLag)
        else:
            self.settings["rel_sequence"].TimeLag = None
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=self.settings["rel_sequence"].RelatedProcess)
