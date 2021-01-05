from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}
    representations = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        cls.products[product_id] = []
        product = file.by_id(product_id)
        if not product.Representation:
            return
        for representation in product.Representation.Representations:
            c = representation.ContextOfItems
            rep_id = int(representation.id())
            cls.representations[rep_id] = {
                "RepresentationIdentifier": representation.RepresentationIdentifier,
                "RepresentationType": representation.RepresentationType,
                "ContextOfItems": {
                    "ContextType": c.ContextType,
                    "ContextIdentifier": c.ContextIdentifier,
                    "TargetView": c.TargetView if c.is_a("IfcGeometricRepresentationSubContext") else "",
                }
            }
            cls.products[product_id].append(rep_id)
