import ifcopenshell


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"layer_set": None, "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        layers = list(self.settings["layer_set"].MaterialLayers or [])
        layer = self.file.create_entity("IfcMaterialLayer", **{
            "Material": self.settings["material"],
            "LayerThickness": 0.
        })
        layers.append(layer)
        self.settings["layer_set"].MaterialLayers = layers
        return layer
