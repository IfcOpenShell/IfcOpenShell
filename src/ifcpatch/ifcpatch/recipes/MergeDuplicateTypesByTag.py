import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        tags = {}
        for element in self.file.by_type("IfcTypeObject"):
            original_element = tags.get(element.Tag, None)
            if original_element:
                for inverse in self.file.get_inverse(element):
                    ifcopenshell.util.element.replace_attribute(inverse, element, original_element)
                self.file.remove(element)
            else:
                tags[element.Tag] = element
