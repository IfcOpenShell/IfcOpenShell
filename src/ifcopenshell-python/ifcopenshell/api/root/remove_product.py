import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        representations = []
        if self.settings["product"].is_a("IfcProduct"):
            if self.settings["product"].Representation:
                representations = self.settings["product"].Representation.Representations or []
            else:
                representations = []
        elif self.settings["product"].is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in self.settings["product"].RepresentationMaps or []]
        for representation in representations:
            ifcopenshell.api.run(
                "geometry.unassign_representation",
                self.file,
                **{"product": self.settings["product"], "representation": representation}
            )
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        for opening in getattr(self.settings["product"], "HasOpenings", []) or []:
            ifcopenshell.api.run("void.remove_opening", self.file, opening=opening.RelatedOpeningElement)

        if self.settings["product"].is_a("IfcGrid"):
            for axis in (
                self.settings["product"].UAxes + self.settings["product"].VAxes + (self.settings["product"].WAxes or ())
            ):
                ifcopenshell.api.run("grid.remove_grid_axis", self.file, axis=axis)

        # TODO: remove object placement and other relationships
        for inverse in self.file.get_inverse(self.settings["product"]):
            if inverse.is_a("IfcRelFillsElement"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelVoidsElement"):
                self.file.remove(inverse)
        self.file.remove(self.settings["product"])
