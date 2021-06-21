import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "products": []}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        quantity_names = set()
        for quantity in self.settings["cost_item"].CostQuantities or []:
            if quantity.Name:
                quantity_names.add(quantity.Name)

        for product in self.settings["products"]:
            ifcopenshell.api.run(
                "control.assign_control",
                self.file,
                related_object=product,
                relating_control=self.settings["cost_item"],
            )

        for name in quantity_names:
            ifcopenshell.api.run(
                "cost.assign_cost_item_product_quantities",
                self.file,
                cost_item=self.settings["cost_item"],
                prop_name=name
            )
