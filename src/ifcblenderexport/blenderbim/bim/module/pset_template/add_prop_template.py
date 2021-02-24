import ifcopenshell


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"pset_template": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        prop_template = self.file.create_entity("IfcSimplePropertyTemplate", **{
            "GlobalId": ifcopenshell.guid.new(),
            "Name": "NewProperty",
            "PrimaryMeasureType": "IfcLabel",
            "TemplateType": "P_SINGLEVALUE",
            "AccessState": "READWRITE"
        })
        has_property_templates = list(self.settings["pset_template"].HasPropertyTemplates) or []
        has_property_templates.append(prop_template)
        self.settings["pset_template"].HasPropertyTemplates = has_property_templates
        return prop_template
