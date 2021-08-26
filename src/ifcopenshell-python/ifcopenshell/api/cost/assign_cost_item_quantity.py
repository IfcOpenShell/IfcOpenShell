import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "products": [], "prop_name": ""}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["prop_name"]:
            self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for product in self.settings["products"]:
            ifcopenshell.api.run(
                "control.assign_control",
                self.file,
                related_object=product,
                relating_control=self.settings["cost_item"],
            )
            if self.settings["prop_name"]:
                self.add_quantity_from_related_object(product)
        if self.settings["prop_name"]:
            self.settings["cost_item"].CostQuantities = list(self.quantities)
        else:
            self.update_cost_item_count()

    def add_quantity_from_related_object(self, element):
        if not element.is_a("IfcObject"):
            return
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                self.add_quantity_from_qto(relationship.RelatingPropertyDefinition)

    def add_quantity_from_qto(self, qto):
        if not qto.is_a("IfcElementQuantity"):
            return
        for prop in qto.Quantities:
            if prop.is_a("IfcPhysicalSimpleQuantity") and prop.Name.lower() == self.settings["prop_name"].lower():
                self.quantities.add(prop)

    def update_cost_item_count(self):
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if not self.settings["cost_item"].CostQuantities:
            return ifcopenshell.api.run(
                "cost.add_cost_item_quantity",
                self.file,
                cost_item=self.settings["cost_item"],
                ifc_class="IfcQuantityCount",
            )
        if len(self.settings["cost_item"].CostQuantities) == 1:
            quantity = self.settings["cost_item"].CostQuantities[0]
            if quantity.is_a("IfcQuantityCount"):
                count = 0
                for rel in self.settings["cost_item"].Controls:
                    count += len(rel.RelatedObjects)
                quantity[3] = count
