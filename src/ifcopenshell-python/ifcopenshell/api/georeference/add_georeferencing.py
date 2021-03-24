class Usecase:
    def __init__(self, file, settings={}):
        self.file = file

    def execute(self):
        source_crs = None
        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.ContextType == "Model":
                source_crs = context
                break
        if not source_crs:
            return
        projected_crs = self.file.create_entity("IfcProjectedCRS", **{"Name": ""})
        self.file.create_entity("IfcMapConversion", **{
            "SourceCRS": source_crs,
            "TargetCRS": projected_crs,
            "Eastings": 0,
            "Northings": 0,
            "OrthogonalHeight": 0,
        })
