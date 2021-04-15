import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None,
            "relating_control": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        has_assignments = None
        if self.settings["related_object"].HasAssignments:
            for assignement in self.settings["related_object"].HasAssignments:
                if assignement.is_a("IfclRelAssignsToControl"):
                    has_assignments = assignement

        controls = None
        for rel in self.settings["relating_control"].Controls:
            if rel.is_a("IfcRelAssignsToControl"):
                controls = rel
                break
        if has_assignments and has_assignments == controls:
            return
        if has_assignments:
            related_objects = list(has_assignments.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                has_assignments.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": has_assignments})
            else:
                self.file.remove(has_assignments)
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
                }
            )
        return controls
