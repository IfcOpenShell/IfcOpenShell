class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"material_set": None, "old_index": 0, "new_index": 0}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["material_set"].is_a("IfcMaterialConstituentSet"):
            set_name = "MaterialConstituents"
        elif self.settings["material_set"].is_a("IfcMaterialLayerSet"):
            set_name = "MaterialLayers"
        elif self.settings["material_set"].is_a("IfcMaterialProfileSet"):
            set_name = "MaterialProfiles"
        elif self.settings["material_set"].is_a("IfcMaterialList"):
            set_name = "Materials"
        items = list(getattr(self.settings["material_set"], set_name) or [])
        items.insert(self.settings["new_index"], items.pop(self.settings["old_index"]))
        setattr(self.settings["material_set"], set_name, items)
