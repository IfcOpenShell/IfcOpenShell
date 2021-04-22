import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_schedule": None, "cost_item": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        cost_item = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcCostItem")

        if self.settings["cost_schedule"]:
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [cost_item],
                    "RelatingControl": self.settings["cost_schedule"],
                }
            )
        elif self.settings["cost_item"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=cost_item, relating_object=self.settings["cost_item"]
            )
        return cost_item
