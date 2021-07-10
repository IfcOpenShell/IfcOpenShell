import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"load_case": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        for rel in self.settings["load_case"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["load_case"])
