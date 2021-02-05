from blenderbim.bim.module.owner.api import update_owner_history


class Usecase():
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "attributes": {}
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["product"], name, value)
        if hasattr(self.settings["product"], "OwnerHistory"):
            update_owner_history(self.settings["product"])
