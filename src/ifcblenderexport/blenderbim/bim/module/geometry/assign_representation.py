class Usecase:
    def __init__(self, file, settings=None):
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
