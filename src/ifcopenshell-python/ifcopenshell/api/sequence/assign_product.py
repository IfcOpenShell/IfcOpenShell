import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_product": None,
            "related_process": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        referenced_by = None

        if self.settings["relating_product"].ReferencedBy:
            for rel in self.settings["relating_product"].ReferencedBy:
                if rel.is_a("IfcRelAssignsToProduct"):
                    referenced_by = rel

        assignment = None
        for rel in self.settings["related_process"].HasAssignments:
            if rel.is_a('IfcRelAssignsToProduct'):
                assignment = rel
                break
        if referenced_by and referenced_by == assignment:
            return

        if assignment:
            related_objects = set(assignment.RelatedObjects)
            related_objects.add(self.settings["relating_product"])
            assignment.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": assignment})
        else:
            rel = self.file.create_entity(
            "IfcRelAssignsToProduct",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingProduct": self.settings["relating_product"],
                "RelatedObjects": [self.settings["related_process"]],
            })
            return rel

        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.remove(self.settings["relating_product"])
            if related_objects:
                referenced_by.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": referenced_by})
            else:
                self.file.remove(referenced_by)

        return rel
