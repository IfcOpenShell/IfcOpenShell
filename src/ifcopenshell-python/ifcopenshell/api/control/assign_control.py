import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_control": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["related_object"].HasAssignments:
            for assignment in self.settings["related_object"].HasAssignments:
                if (
                    assignment.is_a("IfclRelAssignsToControl")
                    and assignment.RelatingControl == self.settings["relating_control"]
                ):
                    return

        controls = None
        if self.settings["relating_control"].Controls:
            controls = self.settings["relating_control"].Controls[0]

        if controls:
            related_objects = list(controls.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            controls.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": controls})
        else:
            controls = self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingControl": self.settings["relating_control"],
                },
            )
        return controls
