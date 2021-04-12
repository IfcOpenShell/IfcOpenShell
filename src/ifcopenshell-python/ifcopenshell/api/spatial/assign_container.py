import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "relating_structure": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        contained_in_structure = self.settings["product"].ContainedInStructure
        contains_elements = self.settings["relating_structure"].ContainsElements

        if contains_elements and contained_in_structure and contained_in_structure[0] == contains_elements[0]:
            return

        if contained_in_structure:
            related_elements = list(contained_in_structure[0].RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                contained_in_structure[0].RelatedElements = related_elements
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contained_in_structure[0]})
            else:
                self.file.remove(contained_in_structure[0])

        if contains_elements:
            related_elements = list(contains_elements[0].RelatedElements)
            related_elements.append(self.settings["product"])
            contains_elements[0].RelatedElements = related_elements
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contains_elements[0]})
        else:
            contains_elements = self.file.create_entity(
                "IfcRelContainedInSpatialStructure",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedElements": [self.settings["product"]],
                    "RelatingStructure": self.settings["relating_structure"],
                }
            )

        if getattr(self.settings["product"], "ObjectPlacement", None):
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                product=self.settings["product"],
                matrix=ifcopenshell.util.placement.get_local_placement(self.settings["product"].ObjectPlacement),
            )
