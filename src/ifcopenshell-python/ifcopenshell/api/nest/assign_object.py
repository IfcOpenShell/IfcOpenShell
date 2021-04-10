import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "object": None,
            "relating_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        nests = None
        if self.settings["object"].Nests:
            nests = self.settings["object"].Nests[0]

        is_nested_by = None
        for rel in self.settings["relating_object"].IsNestedBy:
            if rel.is_a("IfcRelNests"):
                is_nested_by = rel
                break

        if nests and nests == is_nested_by:
            return

        if nests:
            related_objects = list(nests.RelatedObjects)
            related_objects.remove(self.settings["object"])
            if related_objects:
                nests.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": nests})
            else:
                self.file.remove(nests)

        if is_nested_by:
            related_objects = list(is_nested_by.RelatedObjects)
            related_objects.append(self.settings["object"])
            is_nested_by.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_nested_by})
        else:
            is_nested_by = self.file.create_entity(
                "IfcRelNests",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["object"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )
        return is_nested_by
