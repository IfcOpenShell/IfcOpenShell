import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"resource": None, "ifc_class": "IfcQuantityCount"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        quantity = self.file.create_entity(self.settings["ifc_class"], Name="Unnamed")
        quantity[3] = 0.0
        old_quantity = self.settings["resource"].BaseQuantity
        self.settings["resource"].BaseQuantity = quantity
        if old_quantity:
            ifcopenshell.util.element.remove_deep(self.file, old_quantity)
        return quantity
