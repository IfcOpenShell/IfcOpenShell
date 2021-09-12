class Data:
    is_loaded = False
    products = {}
    systems = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.systems = {}

    @classmethod
    def load(cls, file):
        cls.products = {}
        cls.systems = {}
        for system in file.by_type("IfcSystem", include_subtypes=False):
            if system.IsGroupedBy:
                for rel in system.IsGroupedBy:
                    for product in rel.RelatedObjects:
                        cls.products.setdefault(product.id(), []).append(system.id())
            data = system.get_info()
            del data["OwnerHistory"]
            cls.systems[system.id()] = data
        cls.is_loaded = True
