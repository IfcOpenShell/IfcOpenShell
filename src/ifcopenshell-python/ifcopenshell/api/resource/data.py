class Data:
    is_loaded = False
    resources = {}

    @classmethod
    def purge(cls):
        cls.resources = {}

    @classmethod
    def load(cls, file):
        cls.resources = {}
        for resource in file.by_type("IfcResource"):
            data = resource.get_info()
            del data["OwnerHistory"]
            data["IsNestedBy"] = []
            for rel in resource.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects]
            data["ResourceOf"] = []
            for rel in resource.ResourceOf:
                [data["ResourceOf"].append(o.id()) for o in rel.RelatedObjects]
            data["HasContext"] = resource.HasContext[0].RelatingContext.id() if resource.HasContext else None
            cls.resources[resource.id()] = data
        cls.is_loaded=True
