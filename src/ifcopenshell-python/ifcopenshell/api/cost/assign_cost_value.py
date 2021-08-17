import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "cost_rate": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for cost_value in self.settings["cost_item"].CostValues:
            ifcopenshell.api.run(
                "cost.remove_cost_item_value", self.file, parent=self.settings["cost_item"], cost_value=cost_value
            )
        # This is an assumption, and not part of the official IFC documentation
        self.settings["cost_item"].CostValues = self.settings["cost_rate"].CostValues
