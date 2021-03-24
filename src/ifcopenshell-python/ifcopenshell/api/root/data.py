class Data:
    products = {}

    @classmethod
    def purge(cls):
        cls.products = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        product = file.by_id(product_id)
        cls.products[product_id] = {
            "type": product.is_a(),
            "PredefinedType": product.PredefinedType if hasattr(product, "PredefinedType") else None,
            "ObjectType": product.ObjectType if hasattr(product, "ObjectType") else None
        }
