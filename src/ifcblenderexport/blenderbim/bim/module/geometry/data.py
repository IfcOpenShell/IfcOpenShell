from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}
    representations = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.representations = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        cls.products[product_id] = []
        product = file.by_id(product_id)
        representations = []
        if product.is_a("IfcProduct"):
            if product.Representation:
                representations = product.Representation.Representations
            else:
                representations = []
        elif product.is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in product.RepresentationMaps]
        for representation in representations:
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
