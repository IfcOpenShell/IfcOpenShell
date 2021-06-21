import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_product": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        products = set()
        related_object = None
        if self.settings["related_object"]:
            related_object = self.settings["related_object"]
        elif self.settings["relating_product"]:
            for reference in self.settings["relating_product"].ReferencedBy:
                if reference.is_a("IfcRelAssignsToProduct"):
                    related_object = referenced_by.RelatedObjects[0]
        if related_object:
            assignments = self.settings["related_object"].HasAssignments
            for assignment in assignments:
                if assignment.is_a("IfcRelAssignsToProduct"):
                    products.add(assignment.RelatingProduct.id())
        return products
