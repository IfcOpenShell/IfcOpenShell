import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["representation"].RepresentationType == "MappedRepresentation":
            return self.remove_mapped_representation_portion_only()
        return self.remove_entire_representation_tree()

    def remove_mapped_representation_portion_only(self):
        dummy_context = self.file.create_entity("IfcRepresentationContext")
        dummy_representation_map = self.file.createIfcRepresentationMap()
        self.settings["representation"].ContextOfItems = dummy_context
        for item in self.settings["representation"].Items:
            item.MappingSource = dummy_representation_map
        ifcopenshell.util.element.remove_deep(self.file, self.settings["representation"])
        self.file.remove(self.settings["representation"])

    def remove_entire_representation_tree(self):
        dummy_context = self.file.create_entity("IfcRepresentationContext")
        for subelement in self.file.traverse(self.settings["representation"]):
            if subelement.is_a("IfcRepresentationItem") and subelement.StyledByItem:
                [self.file.remove(s) for s in subelement.StyledByItem]
            elif subelement.is_a("IfcRepresentation"):
                subelement.ContextOfItems = dummy_context
                self.purge_representation_inverses(subelement)
        self.purge_representation_inverses(self.settings["representation"])
        ifcopenshell.util.element.remove_deep(self.file, self.settings["representation"])

    def purge_representation_inverses(self, element):
        for inverse in self.file.get_inverse(element):
            if inverse.is_a("IfcPresentationLayerAssignment"):
                assigned_items = set(inverse.AssignedItems)
                if len(assigned_items) == 1:
                    self.file.remove(inverse)
                else:
                    assigned_items.remove(element)
                    inverse.AssignedItems = list(assigned_items)
