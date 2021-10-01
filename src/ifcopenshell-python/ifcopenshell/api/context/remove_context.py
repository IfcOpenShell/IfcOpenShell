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
                if inverse.is_a("IfcCoordinateOperation"):
                    inverse.SourceCRS = inverse.TargetCRS
                    ifcopenshell.util.element.remove_deep(self.file, inverse)
                else:
                    ifcopenshell.util.element.replace_attribute(inverse, self.settings["context"], new)
            self.file.remove(self.settings["context"])
        else:
            representations_in_context = self.settings["context"].RepresentationsInContext
            self.file.remove(self.settings["context"])
            for element in representations_in_context:
                ifcopenshell.api.run("geometry.remove_representation", self.file, representation=element)
