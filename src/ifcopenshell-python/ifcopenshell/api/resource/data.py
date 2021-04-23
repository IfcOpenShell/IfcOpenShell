import ifcopenshell.api


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
            data["RelatedObjects"] = []
            for rel in resource.IsNestedBy:
                [data["RelatedObjects"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcCrewResource") or o.is_a("IfcsubcontractResource")]
            cls.resources[resource.id()] = data

        cls.is_loaded=True
