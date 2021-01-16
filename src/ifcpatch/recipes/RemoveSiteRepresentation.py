class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        project = self.file.by_type('IfcProject')[0]
        sites = self.find_decomposed_ifc_class(project, 'IfcSite')
        for site in sites:
            site.Representation = None

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
