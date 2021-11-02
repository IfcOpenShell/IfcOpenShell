import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None,
            "relating_type": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["relating_type"].RepresentationMaps:
            return
        representations = []
        if self.settings["related_object"].Representation:
            representations = self.settings["related_object"].Representation.Representations
        for representation in representations:
            print('for each rep', representation)
            ifcopenshell.api.run(
                "geometry.unassign_representation",
                self.file,
                product=self.settings["related_object"],
                representation=representation,
            )
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        for representation_map in self.settings["relating_type"].RepresentationMaps:
            representation = representation_map.MappedRepresentation
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", self.file, representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation",
                self.file,
                product=self.settings["related_object"],
                representation=mapped_representation,
            )
