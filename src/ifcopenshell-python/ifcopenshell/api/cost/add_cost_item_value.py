import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "ifc_class": "IfcQuantityCount"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        value = self.file.create_entity("IfcCostValue")
        values = list(self.settings["cost_item"].CostValues or [])
        values.append(value)
        self.settings["cost_item"].CostValues = values
        return value
