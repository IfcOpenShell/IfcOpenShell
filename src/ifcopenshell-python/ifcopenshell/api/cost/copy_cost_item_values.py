import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"source": None, "destination": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for cost_value in self.settings["destination"].CostValues or []:
            ifcopenshell.api.run("cost.remove_cost_item_value", self.file, cost_value=cost_value)
        copied_cost_values = []
        for cost_value in self.settings["source"].CostValues or []:
            copied_cost_values.append(ifcopenshell.util.element.copy_deep(self.file, cost_value))
        self.settings["destination"].CostValues = copied_cost_values
