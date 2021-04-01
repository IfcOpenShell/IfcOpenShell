class Data:
    is_loaded = False
    products = {}
    groups = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.groups = {}

    @classmethod
    def load(cls, file):
        cls.products = {}
        cls.groups = {}
        for group in file.by_type("IfcGroup", include_subtypes=False):
            if group.IsGroupedBy:
                for rel in group.IsGroupedBy:
                    for product in rel.RelatedObjects:
                        cls.products.setdefault(product.id(), []).append(group.id())
            data = group.get_info()
            del data["OwnerHistory"]
            cls.groups[group.id()] = data
        cls.is_loaded=True
