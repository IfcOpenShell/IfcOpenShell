import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"material_list": None, "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        materials = list(self.settings["material_list"].Materials or [])
        materials.append(self.settings["material"])
        self.settings["material_list"].Materials = materials
