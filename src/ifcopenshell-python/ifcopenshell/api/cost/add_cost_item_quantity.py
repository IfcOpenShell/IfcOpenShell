import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "ifc_class": "IfcQuantityCount"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        quantity = self.file.create_entity(self.settings["ifc_class"], Name="Unnamed")
        quantity[3] = 0.0
        cost_item = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcCostItem")
        quantities = list(self.settings["cost_item"].CostQuantities or [])
        quantities.append(quantity)
        self.settings["cost_item"].CostQuantities = quantities
        return quantity
