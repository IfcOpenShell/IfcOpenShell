from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    groups = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.groups = {}

    @classmethod
    def load(cls):
        cls.groups = {}
        for group in IfcStore.get_file().by_type("IfcGroup", include_subtypes=False):
            data = group.get_info()
            del data["OwnerHistory"]
            cls.groups[group.id()] = data
        cls.is_loaded=True
