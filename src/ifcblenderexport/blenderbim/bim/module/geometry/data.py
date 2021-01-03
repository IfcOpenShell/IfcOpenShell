from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        cls.products[product_id] = {"Representations": {}}
        product = file.by_id(product_id)
        if not product.Representation:
            return
        for representation in product.Representation.Representations:
            c = representation.ContextOfItems
            cls.products[product_id]["Representations"][int(representation.id())] = {
                "RepresentationIdentifier": representation.RepresentationIdentifier,
                "RepresentationType": representation.RepresentationType,
                "ContextOfItems": {
                    "ContextType": c.ContextType,
                    "ContextIdentifier": c.ContextIdentifier,
                    "TargetView": c.TargetView if c.is_a("IfcGeometricRepresentationSubContext") else "",
                }
            }
