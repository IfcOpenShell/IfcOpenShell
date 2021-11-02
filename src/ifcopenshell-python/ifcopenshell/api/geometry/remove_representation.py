import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        styled_items = set()
        presentation_layer_assignments = set()
        for subelement in self.file.traverse(self.settings["representation"]):
            if subelement.is_a("IfcRepresentationItem") and subelement.StyledByItem:
                [styled_items.add(s) for s in subelement.StyledByItem]
            elif subelement.is_a("IfcRepresentation"):
                for inverse in self.file.get_inverse(subelement):
                    if inverse.is_a("IfcPresentationLayerAssignment"):
                        presentation_layer_assignments.add(inverse)

        ifcopenshell.util.element.remove_deep2(
            self.file,
            self.settings["representation"],
            also_consider=list(styled_items | presentation_layer_assignments),
            do_not_delete=self.file.by_type("IfcGeometricRepresentationContext"),
        )

        for element in styled_items:
            if not element.Item:
                self.file.remove(element)
        for element in presentation_layer_assignments:
            if len(element.AssignedItems) == 0:
                self.file.remove(element)
