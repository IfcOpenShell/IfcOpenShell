import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcProduct"):
            definition = self.settings["product"].Representation
            if not definition:
                definition = self.file.createIfcProductDefinitionShape()
                self.settings["product"].Representation = definition
            representations = list(definition.Representations) if definition.Representations else []
            representations.append(self.settings["representation"])
            definition.Representations = representations
        elif self.settings["product"].is_a("IfcTypeProduct"):
            if self.settings["product"].RepresentationMaps:
                maps = list(self.settings["product"].RepresentationMaps)
            else:
                maps = []
            self.zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            self.x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
            self.z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))
            maps.append(
                self.file.create_entity(
                    "IfcRepresentationMap",
                    **{
                        "MappingOrigin": self.file.createIfcAxis2Placement3D(self.zero, self.z_axis, self.x_axis),
                        "MappedRepresentation": self.settings["representation"],
                    }
                )
            )
            self.settings["product"].RepresentationMaps = maps
            if self.file.schema == "IFC2X3":
                types = self.settings["product"].ObjectTypeOf
            else:
                types = self.settings["product"].Types
            if types:
                for element in types[0].RelatedObjects:
                    mapped_representation = ifcopenshell.api.run(
                        "geometry.map_representation", self.file, **{"representation": self.settings["representation"]}
                    )
                    ifcopenshell.api.run(
                        "geometry.assign_representation",
                        self.file,
                        **{"product": element, "representation": mapped_representation}
                    )
        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": self.settings["product"]})
