class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"shape_representation": None, "styles": []}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["styles"]:
            return []
        self.results = []
        for element in self.file.traverse(self.settings["shape_representation"]):
            if not element.is_a("IfcShapeRepresentation"):
                continue
            for item in element.Items:
                if not item.is_a("IfcGeometricRepresentationItem"):
                    continue
                style = self.settings["styles"].pop(0)
                self.results.append(
                    self.file.createIfcStyledItem(
                        item, [style], style.Name
                    )
                )
        return self.results
