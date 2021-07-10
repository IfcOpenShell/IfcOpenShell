import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        for inverse in self.file.get_inverse(self.settings["cost_item"]):
            if inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["cost_item"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run("cost.remove_cost_item", self.file, cost_item=related_object)
                elif inverse.RelatedObjects == tuple(self.settings["cost_item"]):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                self.file.remove(inverse)
        self.file.remove(self.settings["cost_item"])
