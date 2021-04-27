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
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if self.settings["ifc_class"] == "IfcQuantityCount" and self.settings["cost_item"].Controls:
            for rel in self.settings["cost_item"].Controls:
                quantity[3] += len(rel.RelatedObjects)
        quantities = list(self.settings["cost_item"].CostQuantities or [])
        quantities.append(quantity)
        self.settings["cost_item"].CostQuantities = quantities
        return quantity
