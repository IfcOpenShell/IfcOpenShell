class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"parent": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        value = self.file.create_entity("IfcCostValue")
        if self.settings["parent"].is_a("IfcCostItem"):
            values = list(self.settings["parent"].CostValues or [])
            values.append(value)
            self.settings["parent"].CostValues = values
        elif self.settings["parent"].is_a("IfcConstructionResource"):
            values = list(self.settings["parent"].BaseCosts or [])
            values.append(value)
            self.settings["parent"].BaseCosts = values
        elif self.settings["parent"].is_a("IfcCostValue"):
            values = list(self.settings["parent"].Components or [])
            values.append(value)
            self.settings["parent"].Components = values
        return value
