import ifcopenshell


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        result = self.file.create_entity(self.settings["product"].is_a())
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(self.file.schema)
        self.copy_attributes(self.settings["product"], result)
        for inverse in self.file.get_inverse(self.settings["product"]):
            for i, value in enumerate(inverse):
                if value == self.settings["product"]:
                    new_inverse = self.file.create_entity(inverse.is_a())
                    self.copy_attributes(inverse, new_inverse)
                    new_inverse[i] = result
                elif isinstance(value, (tuple, list)) and self.settings["product"] in value:
                    new_value = list(value)
                    new_value.append(result)
                    inverse[i] = new_value
        if result.is_a("IfcProduct"):
            result.Representation = None
        elif result.is_a("IfcTypeProduct"):
            result.RepresentationMaps = None
        return result

    def copy_attributes(self, from_element, to_element):
        declaration = self.schema.declaration_by_name(from_element.is_a())
        for attribute in declaration.all_attributes():
            if attribute.name() == "GlobalId":
                setattr(to_element, attribute.name(), ifcopenshell.guid.new())
            else:
                setattr(to_element, attribute.name(), getattr(from_element, attribute.name()))
