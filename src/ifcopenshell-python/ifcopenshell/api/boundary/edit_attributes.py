class Usecase:
    def __init__(self, file, **kwargs):
        """location, axis and ref_direction defines the plane"""
        self.file = file
        self.entity: "IfcRelSpaceBoundary"
        self.relating_space: "IfcSpace | IfcExternalSpatialElement"
        self.related_building_element: "IfcElement"
        self.parent_boundary: "IfcRelSpaceBoundary" = None
        self.corresponding_boundary: "IfcRelSpaceBoundary" = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def execute(self):
        self.entity.RelatingSpace = self.relating_space
        self.entity.RelatedBuildingElement = self.related_building_element
        if hasattr(self.entity, "ParentBoundary"):
            self.entity.ParentBoundary = self.parent_boundary
        if hasattr(self.entity, "CorrespondingBoundary"):
            self.entity.CorrespondingBoundary = self.corresponding_boundary
