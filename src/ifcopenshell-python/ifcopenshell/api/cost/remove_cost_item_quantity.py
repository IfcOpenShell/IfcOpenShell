class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None, "physical_quantity": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if len(self.file.get_inverse(self.settings["physical_quantity"])) == 1:
            self.file.remove(self.settings["physical_quantity"])
            return
        quantities = list(self.settings["cost_item"].CostQuantities or [])
        quantities.remove(self.settings["physical_quantity"])
        self.settings["cost_item"].CostQuantities = quantities
