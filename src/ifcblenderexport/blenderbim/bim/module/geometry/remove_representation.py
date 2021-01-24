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
        ifcopenshell.util.element.remove_deep(self.file, self.settings["representation"])
