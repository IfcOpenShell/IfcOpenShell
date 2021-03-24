import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "pset_template": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        ifcopenshell.util.element.remove_deep(self.file, self.settings["pset_template"])
