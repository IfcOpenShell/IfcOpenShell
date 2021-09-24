import ifcopenshell
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(self.file.schema)
        result = ifcopenshell.util.element.copy(self.file, self.settings["product"])
        self.copy_indirect_attributes(self.settings["product"], result)
        # Copying representations is too hard, so for now we just don't do it.
        self.remove_representations(result)
        return result

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
            elif inverse.is_a("IfcRelFillsElement"):
                continue
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
