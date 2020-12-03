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
        for element in selector.parse(self.file, self.args[0]):
            self.add_element(element)
        self.create_spatial_tree()
        self.file = self.new

    def add_element(self, element):
        new_element = self.new.add(element)
        for rel in element.ContainedInStructure:
            spatial_element = rel.RelatingStructure
            new_spatial_element = self.new.add(spatial_element)
            self.contained_ins.setdefault(spatial_element.GlobalId, set()).add(new_element)
            self.add_spatial_tree(spatial_element, new_spatial_element)

    def add_spatial_tree(self, spatial_element, new_spatial_element):
        for rel in spatial_element.Decomposes:
            new = self.new.add(rel.RelatingObject)
            self.aggregates.setdefault(rel.RelatingObject.GlobalId, set()).add(new_spatial_element)
            self.add_spatial_tree(rel.RelatingObject, new)

    def create_spatial_tree(self):
        for relating_structure, related_elements in self.contained_ins.items():
            self.new.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(),
                self.owner_history,
                None,
                None,
                list(related_elements),
                self.new.by_guid(relating_structure),
            )
        for relating_object, related_objects in self.aggregates.items():
            self.new.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                self.owner_history,
                None,
                None,
                self.new.by_guid(relating_object),
                list(related_objects),
            )
