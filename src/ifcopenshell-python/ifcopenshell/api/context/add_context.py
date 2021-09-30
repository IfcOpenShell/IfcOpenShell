class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "context_type": None,
            "parent": None,
            "context_identifier": None,
            "target_view": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["parent"]:
            if self.settings["context_type"] == "Plan":
                self.create_2d_origin()
                context = self.file.createIfcGeometricRepresentationContext(None, "Plan", 2, 1.0e-05, self.origin)
            else:
                self.create_3d_origin()
                context = self.file.createIfcGeometricRepresentationContext(
                    None, self.settings["context_type"], 3, 1.0e-05, self.origin
                )

            project = self.file.by_type("IfcProject")[0]

            if project.RepresentationContexts:
                contexts = list(project.RepresentationContexts)
            else:
                contexts = []
            contexts.append(context)
            project.RepresentationContexts = contexts
            return context
        return self.file.create_entity(
            "IfcGeometricRepresentationSubContext",
            **{
                "ContextIdentifier": self.settings["context_identifier"],
                "ContextType": self.settings["context_type"],
                "ParentContext": self.settings["parent"],
                "TargetView": self.settings["target_view"],
            }
        )

    def create_3d_origin(self):
        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )

    def create_2d_origin(self):
        self.origin = self.file.createIfcAxis2Placement2D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
