class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"connection": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["connection"].is_a("IfcStructuralPointConnection"):
            boundary_class = "IfcBoundaryNodeCondition"
        elif self.settings["connection"].is_a("IfcStructuralCurveConnection"):
            boundary_class = "IfcBoundaryEdgeCondition"
        elif self.settings["connection"].is_a("IfcStructuralSurfaceConnection"):
            boundary_class = "IfcBoundaryFaceCondition"
        self.settings["connection"].AppliedCondition = self.file.create_entity(boundary_class)
