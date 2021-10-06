import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
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

        container = ifcopenshell.util.element.get_container(self.settings["product"], should_get_direct=True)
        if container:
            ifcopenshell.api.run("spatial.remove_container", self.file, product=self.settings["product"])

        if decomposes:
            related_objects = list(decomposes.RelatedObjects)
            related_objects.remove(self.settings["product"])
            if related_objects:
                decomposes.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": decomposes})
            else:
                self.file.remove(decomposes)

        if is_decomposed_by:
            related_objects = set(is_decomposed_by.RelatedObjects)
            related_objects.add(self.settings["product"])
            is_decomposed_by.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_decomposed_by})
        else:
            is_decomposed_by = self.file.create_entity(
                "IfcRelAggregates",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )

        placement = getattr(self.settings["product"], "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                product=self.settings["product"],
                matrix=ifcopenshell.util.placement.get_local_placement(self.settings["product"].ObjectPlacement),
                is_si=False,
            )

        return is_decomposed_by
