import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"resource": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        old_quantity = self.settings["resource"].BaseQuantity
        self.settings["resource"].BaseQuantity = None
        if old_quantity:
            ifcopenshell.util.element.remove_deep(self.file, old_quantity)
