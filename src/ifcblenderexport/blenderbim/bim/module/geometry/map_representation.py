class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "representation": None,
        }
        self.ifc_vertices = []
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        self.x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
        self.y_axis = self.file.createIfcDirection((0.0, 1.0, 0.0))
        self.z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))

        self.get_mapping_source()

        mapping_target = self.file.createIfcCartesianTransformationOperator3D(
            self.x_axis, self.y_axis, self.zero, 1, self.z_axis
        )
        mapped_item = self.file.createIfcMappedItem(self.get_mapping_source(), mapping_target)
        return self.file.create_entity(
            "IfcShapeRepresentation",
            **{
                "ContextOfItems": self.settings["representation"].ContextOfItems,
                "RepresentationIdentifier": self.settings["representation"].RepresentationIdentifier,
                "RepresentationType": "MappedRepresentation",
                "Items": [mapped_item],
            }
        )

    def get_mapping_source(self):
        if self.settings["representation"].RepresentationMap:
            return self.settings["representation"].RepresentationMap[0]
        return self.file.create_entity(
            "IfcRepresentationMap",
            **{
                "MappingOrigin": self.file.createIfcAxis2Placement3D(self.zero, self.z_axis, self.x_axis),
                "MappedRepresentation": self.settings["representation"],
            }
        )
