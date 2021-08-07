class Data:
    products = {}
    types = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.types = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        cls.file = file
        product = file.by_id(product_id)
        if product.is_a("IfcTypeObject"):
            cls.load_type(product_id)
        else:
            cls.load_product(product_id)

    @classmethod
    def load_type(cls, product_id):
        product = cls.file.by_id(product_id)
        cls.types[product_id] = None
        if cls.file.schema == "IFC2X3":
            if getattr(product, "ObjectTypeOf", None):
                cls.types[product_id] = [o.id() for o in product.ObjectTypeOf[0].RelatedObjects]
        else:
            if getattr(product, "Types", None):
                cls.types[product_id] = [o.id() for o in product.Types[0].RelatedObjects]

    @classmethod
    def load_product(cls, product_id):
        product = cls.file.by_id(product_id)
        if cls.file.schema == "IFC2X3" and not hasattr(product, "IsDefinedBy"):
            cls.products[product_id] = None
        elif cls.file.schema != "IFC2X3" and not hasattr(product, "IsTypedBy"):
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
