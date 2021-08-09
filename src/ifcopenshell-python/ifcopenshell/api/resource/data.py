class Data:
    is_loaded = False
    resources = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.resources = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_resources()
        cls.is_loaded=True

    @classmethod
    def load_resources(cls):
        cls.resources = {}
        for resource in cls._file.by_type("IfcResource"):
            data = resource.get_info()
            del data["OwnerHistory"]
            data["IsNestedBy"] = []
            for rel in resource.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects]
            data["Nests"] = []
            for rel in resource.Nests:
                [data["Nests"].append(rel.RelatingObject.id())]
            data["ResourceOf"] = []
            for rel in resource.ResourceOf:
                [data["ResourceOf"].append(o.id()) for o in rel.RelatedObjects]
            data["HasContext"] = resource.HasContext[0].RelatingContext.id() if resource.HasContext else None
            cls.resources[resource.id()] = data
