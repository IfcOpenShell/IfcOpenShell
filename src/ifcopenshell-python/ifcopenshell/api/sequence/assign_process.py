import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_process": None,
            "related_object": None,
            "quantity_in_process": None
        }

        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["related_object"].HasAssignments:
            for assignment in self.settings["related_object"].HasAssignments:
                if (
                    assignment.is_a("IfclRelAssignsToProcess")
                    and assignment.RelatingProcess == self.settings["relating_process"]
                ):
                    return

        operates_on = None
        if self.settings["relating_process"].OperatesOn:
            operates_on = self.settings["relating_process"].OperatesOn[0]

        if operates_on:
            related_objects = list(operates_on.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            operates_on.RelatedObjects = related_objects
            operates_on.QuantityInProcess = self.settings["quantity_in_process"]
            print("op on 1st case", operates_on)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": operates_on})
        else:
            print("settings", self.settings)
            operates_on = self.file.create_entity(
                "IfcRelAssignsToProcess",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingProcess": self.settings["relating_process"],
                    "QuantityInProcess": self.settings["quantity_in_process"]
                }
            )
        return operates_on
