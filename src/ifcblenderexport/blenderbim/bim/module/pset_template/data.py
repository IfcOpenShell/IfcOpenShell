from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    pset_templates = {}
    prop_templates = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.pset_templates = {}
        cls.prop_templates = {}

    @classmethod
    def load(cls):
        cls._file = IfcStore.pset_template_file

        cls.pset_templates = {}
        cls.prop_templates = {}

        for pset_template in cls._file.by_type("IfcPropertySetTemplate"):
            data = pset_template.get_info()
            data["HasPropertyTemplates"] = [e.id() for e in pset_template.HasPropertyTemplates or []]
            if "OwnerHistory" in data:
                del data["OwnerHistory"]
            cls.pset_templates[pset_template.id()] = data

        for prop_template in cls._file.by_type("IfcSimplePropertyTemplate"):
            data = prop_template.get_info()
            cls.prop_templates[prop_template.id()] = {
                "GlobalId": data["GlobalId"],
                "Name": data["Name"],
                "Description": data["Description"],
                "PrimaryMeasureType": data["PrimaryMeasureType"]
            }
        cls.is_loaded = True
