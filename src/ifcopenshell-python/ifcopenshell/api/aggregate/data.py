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
        if product.Decomposes and product.Decomposes[0].is_a("IfcRelAggregates"):
            obj = product.Decomposes[0].RelatingObject
            cls.products[product_id] = {"type": obj.is_a(), "Name": obj.Name, "id": int(obj.id())}
        else:
            cls.products[product_id] = {"type": None, "Name": None, "id": None}
