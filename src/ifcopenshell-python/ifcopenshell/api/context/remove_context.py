import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"context": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for subcontext in self.settings["context"].HasSubContexts:
            ifcopenshell.api.run("context.remove_context", self.file, context=subcontext)

        if getattr(self.settings["context"], "ParentContext", None):
            new = self.settings["context"].ParentContext
            for inverse in self.file.get_inverse(self.settings["context"]):
                ifcopenshell.util.element.replace_attribute(inverse, self.settings["context"], new)

        representations_in_context = self.settings["context"].RepresentationsInContext
        has_coordinate_operation = []
        if self.settings["context"].is_a("IfcGeometricRepresentationSubContext"):
            has_coordinate_operation = self.settings["context"].HasCoordinateOperation

        self.file.remove(self.settings["context"])

        for element in representations_in_context:
            ifcopenshell.api.run("geometry.remove_representation", self.file, representation=element)

        for element in has_coordinate_operation:
            ifcopenshell.util.element.remove_deep(self.file, element)
