import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_resource": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["related_object"].HasAssignments:
            for assignment in self.settings["related_object"].HasAssignments:
                if (
                    assignment.is_a("IfclRelAssignsToResource")
                    and assignment.RelatingResource == self.settings["relating_resource"]
                ):
                    return

        resource_of = None
        if self.settings["relating_resource"].ResourceOf:
            resource_of = self.settings["relating_resource"].ResourceOf[0]

        if resource_of:
            related_objects = list(resource_of.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            resource_of.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": resource_of})
        else:
            resource_of = self.file.create_entity(
                "IfcRelAssignsToResource",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingProduct": self.settings["relating_resource"],
                }
            )
        return resource_of
