import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
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

        if contains_elements and contained_in_structure == contains_elements:
            return

        if contained_in_structure:
            related_elements = list(contained_in_structure[0].RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                contained_in_structure[0].RelatedElements = related_elements
            else:
                self.file.remove(contained_in_structure)

        if contains_elements:
            related_elements = list(contains_elements[0].RelatedElements)
            related_elements.append(self.settings["product"])
            contains_elements[0].RelatedElements = related_elements
        else:
            contains_elements = self.file.create_entity(
                "IfcRelContainedInSpatialStructure",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    # TODO "OwnerHistory": None
                    "RelatedElements": [self.settings["product"]],
                    "RelatingStructure": self.settings["relating_structure"],
                }
            )
