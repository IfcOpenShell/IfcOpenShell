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
            ifcopenshell.api.run("owner.unassign_representation",
                self.file, **{"product": self.settings["product"], "representation": representation}
            )
            ifcopenshell.api.run("owner.remove_representation", self.file, **{"representation": representation})
        # TODO: remove object placement and other relationships
        self.file.remove(self.settings["product"])
