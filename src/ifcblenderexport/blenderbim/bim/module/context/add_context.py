class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "context": None,
            "subcontext": None,
            "target_view": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        parent = [
            c
            for c in self.file.by_type("IfcGeometricRepresentationContext")
            if c.ContextType == self.settings["context"]
        ]
        if not parent:
            self.create_origin()
            if self.settings["context"] == "Plan":
                return self.file.createIfcGeometricRepresentationContext(None, "Plan", 2, 1.0e-05, self.origin)
            return self.file.createIfcGeometricRepresentationContext(None, "Model", 3, 1.0e-05, self.origin)
        parent = parent[0]
        return self.file.create_entity("IfcGeometricRepresentationSubContext", **{
            "ContextIdentifier": self.settings["subcontext"],
            "ContextType": self.settings["context"],
            "ParentContext": parent,
            "TargetView": self.settings["target_view"],
        })

    def create_origin(self):
        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
