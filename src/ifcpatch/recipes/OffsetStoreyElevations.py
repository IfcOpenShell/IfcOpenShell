class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        project = self.file.by_type('IfcProject')[0]
        storeys = self.find_decomposed_ifc_class(project, 'IfcBuildingStorey')
        for storey in storeys:
            co = storey.ObjectPlacement.RelativePlacement.Location.Coordinates
            storey.ObjectPlacement.RelativePlacement.Location.Coordinates = (co[0], co[1], co[2]+float(self.args[0]))
            co = storey.ObjectPlacement.RelativePlacement.Location.Coordinates
            # NOTE  If the geometric data is provided (ObjectPlacement is
            # specified), the Elevation value shall either not be included, or
            # be equal to the local placement Z value.
            storey.Elevation = co[2]

    def find_decomposed_ifc_class(self, element, ifc_class):
        results = []
        rel_aggregates = element.IsDecomposedBy
        if not rel_aggregates:
            return results
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                if part.is_a(ifc_class):
                    results.append(part)
                results.extend(self.find_decomposed_ifc_class(part, ifc_class))
        return results
