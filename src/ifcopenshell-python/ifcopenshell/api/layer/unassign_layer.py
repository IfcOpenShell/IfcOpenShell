import ifcopenshell


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "item": None,
            "layer": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        assigned_items = set(self.settings["layer"].AssignedItems) or set()
        assigned_items.remove(self.settings["item"])
        self.settings["layer"].AssignedItems = list(assigned_items)
