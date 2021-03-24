import ifcopenshell.api.geometry.unassign_representation as unassign_representation
import ifcopenshell.api.geometry.remove_representation as remove_representation


class Usecase:
    def __init__(self, file, settings=None):
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
            unassign_representation.Usecase(
                self.file, {"product": self.settings["product"], "representation": representation}
            ).execute()
            remove_representation.Usecase(self.file, {"representation": representation}).execute()
        # TODO: remove object placement and other relationships
        self.file.remove(self.settings["product"])
