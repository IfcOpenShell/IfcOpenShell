import ifcopenshell
from blenderbim.bim.module.owner.api import create_owner_history
from blenderbim.bim.module.owner.api import update_owner_history


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "relating_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        decomposes = None
        if self.settings["product"].Decomposes:
            decomposes = self.settings["product"].Decomposes[0]

        is_decomposed_by = None
        for rel in self.settings["relating_object"].IsDecomposedBy:
            if rel.is_a("IfcRelAggregates"):
                is_decomposed_by = rel
                break

        if decomposes and decomposes == is_decomposed_by:
            return

        if decomposes:
            related_objects = list(decomposes.RelatedObjects)
            related_objects.remove(self.settings["product"])
            if related_objects:
                decomposes.RelatedObjects = related_objects
                update_owner_history(decomposes)
            else:
                self.file.remove(decomposes)

        if is_decomposed_by:
            related_objects = list(is_decomposed_by.RelatedObjects)
            related_objects.append(self.settings["product"])
            is_decomposed_by.RelatedObjects = related_objects
            update_owner_history(is_decomposed_by)
        else:
            is_decomposed_by = self.file.create_entity(
                "IfcRelAggregates",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": create_owner_history(),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )
