import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material_list": None, "material_index": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        materials = list(self.settings["material_list"].Materials)
        materials.pop(self.settings["material_index"])
        self.settings["material_list"].Materials = materials
