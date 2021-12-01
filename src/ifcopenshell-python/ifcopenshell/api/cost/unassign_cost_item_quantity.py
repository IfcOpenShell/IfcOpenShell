import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "products": []}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for quantity in self.settings["cost_item"].CostQuantities or []:
            for inverse in self.file.get_inverse(quantity):
                if not inverse.is_a("IfcElementQuantity"):
                    continue
                for rel in inverse.DefinesOccurrence or []:
                    for related_object in rel.RelatedObjects:
                        if related_object in self.settings["products"]:
                            self.quantities.remove(quantity)
        self.settings["cost_item"].CostQuantities = list(self.quantities)
        for product in self.settings["products"]:
            ifcopenshell.api.run(
                "control.unassign_control",
                self.file,
                related_object=product,
                relating_control=self.settings["cost_item"],
            )
        self.update_cost_item_count()

    def update_cost_item_count(self):
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if len(self.settings["cost_item"].CostQuantities) == 1:
            quantity = self.settings["cost_item"].CostQuantities[0]
            if quantity.is_a("IfcQuantityCount"):
                count = 0
                for rel in self.settings["cost_item"].Controls:
                    count += len(rel.RelatedObjects)
                quantity[3] = count
