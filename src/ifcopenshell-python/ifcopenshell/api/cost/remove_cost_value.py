class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"parent": None, "cost_value": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if len(self.file.get_inverse(self.settings["cost_value"])) == 1:
            self.file.remove(self.settings["cost_value"])
            # TODO deep purge
        elif self.settings["parent"].is_a("IfcCostItem"):
            values = list(self.settings["parent"].CostValues)
            values.remove(self.settings["cost_value"])
            self.settings["parent"].CostValues = values if values else None
        elif self.settings["parent"].is_a("IfcConstructionResource"):
            values = list(self.settings["parent"].BaseCosts)
            values.remove(self.settings["cost_value"])
            self.settings["parent"].BaseCosts = values if values else None
        elif self.settings["parent"].is_a("IfcCostValue"):
            components = list(self.settings["parent"].Components)
            components.remove(self.settings["cost_value"])
            self.settings["parent"].Components = components if components else None
