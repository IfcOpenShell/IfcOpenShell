class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"layer_set": None, "old_index": 0, "new_index": 0}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        layers = list(self.settings["layer_set"].MaterialLayers or [])
        layers.insert(self.settings["new_index"], layers.pop(self.settings["old_index"]))
        self.settings["layer_set"].MaterialLayers = layers
