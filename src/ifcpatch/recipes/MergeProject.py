import ifcopenshell
import ifcopenshell.util.element

class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        source = ifcopenshell.open(self.args[0])
        original_project = self.file.by_type('IfcProject')[0]
        merged_project = self.file.add(source.by_type('IfcProject')[0])
        for element in source.by_type('IfcRoot'):
            self.file.add(element)
        for inverse in self.file.get_inverse(merged_project):
            ifcopenshell.util.element.replace_attribute(inverse, merged_project, original_project)
        self.file.remove(merged_project)
