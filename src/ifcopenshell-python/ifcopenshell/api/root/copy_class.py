import ifcopenshell
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        result = ifcopenshell.util.element.copy(self.file, self.settings["product"])
        self.copy_direct_attributes(result)
        self.copy_indirect_attributes(self.settings["product"], result)
        return result

    def copy_direct_attributes(self, to_element):
        self.remove_representations(to_element)
        self.copy_object_placements(to_element)

    def copy_indirect_attributes(self, from_element, to_element):
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                # Properties must not be shared between objects for convenience of authoring
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(self.file, inverse.RelatingPropertyDefinition)
                inverse.RelatingPropertyDefinition = pset
            elif inverse.is_a("IfcRelAggregates") and inverse.RelatingObject == from_element:
                continue
            elif inverse.is_a("IfcRelContainedInSpatialStructure") and inverse.RelatingStructure == from_element:
                continue
            elif inverse.is_a("IfcRelFillsElement"):
                continue
            elif inverse.is_a("IfcRelAssociatesMaterial") and "Usage" in inverse.RelatingMaterial.is_a():
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatingMaterial = ifcopenshell.util.element.copy(self.file, inverse.RelatingMaterial)
                inverse.RelatedObjects = [to_element]
            else:
                for i, value in enumerate(inverse):
                    if value == from_element:
                        new_inverse = ifcopenshell.util.element.copy(self.file, inverse)
                        new_inverse[i] = to_element
                    elif isinstance(value, (tuple, list)) and from_element in value:
                        new_value = list(value)
                        new_value.append(to_element)
                        inverse[i] = new_value

    def remove_representations(self, element):
        if element.is_a("IfcProduct"):
            element.Representation = None
        elif element.is_a("IfcTypeProduct"):
            element.RepresentationMaps = None

    def copy_object_placements(self, element):
        if not element.is_a("IfcProduct") or not element.ObjectPlacement:
            return
        element.ObjectPlacement = ifcopenshell.util.element.copy(self.file, element.ObjectPlacement)
        element.ObjectPlacement.RelativePlacement = ifcopenshell.util.element.copy_deep(
            self.file, element.ObjectPlacement.RelativePlacement
        )
