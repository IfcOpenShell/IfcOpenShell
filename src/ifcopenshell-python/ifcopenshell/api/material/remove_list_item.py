import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material_list": None, "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        materials = [m for m in self.settings["material_list"].Materials if m != self.settings["material"]]
        self.settings["material_list"].Materials = materials
