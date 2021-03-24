class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"representation": None}
        self.ifc_vertices = []
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        mapping_source = self.get_mapping_source()

        if not mapping_source:
            return

        zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
        y_axis = self.file.createIfcDirection((0.0, 1.0, 0.0))
        z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))

        mapping_target = self.file.createIfcCartesianTransformationOperator3D(x_axis, y_axis, zero, 1, z_axis)
        mapped_item = self.file.createIfcMappedItem(mapping_source, mapping_target)
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
        for inverse in self.file.get_inverse(self.settings["representation"]):
            if inverse.is_a("IfcRepresentationMap"):
                return inverse
