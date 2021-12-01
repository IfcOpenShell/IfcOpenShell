import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"opening": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["opening"].VoidsElements:
            self.file.remove(rel)
        for rel in self.settings["opening"].HasFillings:
            self.file.remove(rel)
        ifcopenshell.api.run("root.remove_product", self.file, product=self.settings["opening"])
