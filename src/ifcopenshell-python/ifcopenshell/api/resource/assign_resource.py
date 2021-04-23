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

        referenced_by = None
        if self.settings["relating_resource"].ResourceOf:
            referenced_by = self.settings["relating_resource"].ResourceOf[0]

        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            referenced_by.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": referenced_by})
        else:
            referenced_by = self.file.create_entity(
                "IfcRelAssignsToResource",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingProduct": self.settings["relating_resource"],
                }
            )
        return referenced_by
