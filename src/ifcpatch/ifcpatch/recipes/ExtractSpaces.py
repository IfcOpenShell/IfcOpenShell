import ifcopenshell
import ifcopenshell.util.selector


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        self.contained_ins = {}
        self.aggregates = {}
        self.new = ifcopenshell.file(schema=self.file.wrapped_data.schema)
        self.owner_history = None
        for owner_history in self.file.by_type("IfcOwnerHistory"):
            self.owner_history = self.new.add(owner_history)
            break
        selector = ifcopenshell.util.selector.Selector()
        for space in selector.parse(self.file, ".IfcSpace"):
            self.add_element(space)
        self.file = self.new

    def add_element(self, element):
        self.new.add(element)
        for rel_aggregate in element.Decomposes:
            self.add_element(rel_aggregate.RelatingObject)
            self.new.add(rel_aggregate)
