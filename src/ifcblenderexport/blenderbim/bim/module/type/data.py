from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}

    @classmethod
    def purge(cls):
        cls.products = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        if file.schema == "IFC2X3" and not hasattr(product, "IsDefinedBy"):
            cls.products[product_id] = None
        elif file.schema != "IFC2X3" and not hasattr(product, "IsTypedBy"):
            cls.products[product_id] = None
        elif hasattr(product, "IsTypedBy") and product.IsTypedBy:
            type = product.IsTypedBy[0].RelatingType
            cls.products[product_id] = {"type": type.is_a(), "Name": type.Name, "id": int(type.id())}
        elif hasattr(product, "IsDefinedBy") and product.IsDefinedBy:
            cls.products[product_id] = {"type": None, "Name": None}
            for rel in product.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByType"):
                    type = rel.RelatingType
                    cls.products[product_id] = {"type": type.is_a(), "Name": type.Name, "id": int(type.id())}
        else:
            cls.products[product_id] = {"type": None, "Name": None, "id": None}
