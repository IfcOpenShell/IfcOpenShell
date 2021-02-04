import ifcopenshell.util.element

class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
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
                    inverse.AssignedItems == list(assigned_items)
            elif inverse.is_a("IfcProductRepresentation"):
                representations = set(inverse.Representations)
                if len(representations) == 1:
                    self.file.remove(inverse)
                else:
                    representations.remove(element)
                    inverse.Representations = list(representations)
