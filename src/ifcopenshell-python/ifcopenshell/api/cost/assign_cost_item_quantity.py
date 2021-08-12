import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "products": [], "prop_name": ""}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for product in self.settings["products"]:
            ifcopenshell.api.run(
                "control.assign_control",
                self.file,
                related_object=product,
                relating_control=self.settings["cost_item"],
            )
            self.add_quantity_from_related_object(product)
        self.settings["cost_item"].CostQuantities = list(self.quantities)

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
