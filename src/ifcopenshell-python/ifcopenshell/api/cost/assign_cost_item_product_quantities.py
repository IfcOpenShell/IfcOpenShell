import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "qto_name": "", "prop_name": ""}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for control in self.settings["cost_item"].Controls or []:
            for related_object in control.RelatedObjects:
                self.add_quantity_from_related_object(related_object)
        self.settings["cost_item"].CostQuantities = list(self.quantities)

    def add_quantity_from_related_object(self, element):
        if element.is_a("IfcTypeObject"):
            for definition in element.HasPropertySets or []:
                self.add_quantity_from_qto(definition)
        else:
            for relationship in element.IsDefinedBy:
                if relationship.is_a("IfcRelDefinesByProperties"):
                    self.add_quantity_from_qto(relationship.RelatingPropertyDefinition)

    def add_quantity_from_qto(self, qto):
        if not qto.is_a("IfcElementQuantity") or qto.Name.lower() != self.settings["qto_name"].lower():
            return
        for prop in qto.Quantities:
            if prop.is_a("IfcPhysicalSimpleQuantity") and prop.Name.lower() == self.settings["prop_name"].lower():
                self.quantities.add(prop)
