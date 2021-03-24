import blenderbim.bim.schema  # TODO: refactor


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"qto": None, "Name": None, "Properties": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.update_qto_name()
        self.load_qto_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_qto_with_new_properties(new_properties)

    def update_qto_name(self):
        if self.settings["Name"]:
            self.settings["qto"].Name = self.settings["Name"]

    def load_qto_template(self):
        self.qto_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(self.settings["qto"].Name)

    def update_existing_properties(self):
        for prop in self.settings["qto"].Quantities or []:
            self.update_existing_property(prop)

    def update_existing_property(self, prop):
        if prop.Name not in self.settings["Properties"]:
            return
        value = self.settings["Properties"][prop.Name]
        if prop.is_a("IfcPhysicalSimpleQuantity"):
            prop[3] = float(value) if value else None
        del self.settings["Properties"][prop.Name]

    def add_new_properties(self):
        properties = []
        for name, value in self.settings["Properties"].items():
            if value is None:
                continue
            property_type = self.get_canonical_property_type(name)
            properties.append(
                self.file.create_entity(
                    "IfcQuantity{}".format(property_type),
                    **{"Name": name, "{}Value".format(property_type): value},
                )
            )
        return properties

    def extend_qto_with_new_properties(self, new_properties):
        props = list(self.settings["qto"].Quantities) if self.settings["qto"].Quantities else []
        props.extend(new_properties)
        self.settings["qto"].Quantities = props

    def get_canonical_property_type(self, name):
        if not self.qto_template:
            return "Length"
        for prop_template in self.qto_template.HasPropertyTemplates:
            if prop_template.Name != name:
                continue
            return prop_template.TemplateType[2:].lower().capitalize()
        return "Length"

    def get_primary_measure_type(self, name, previous_value=None):
        if not self.qto_template:
            return previous_value.is_a() if previous_value else "IfcLabel"
        for prop_template in self.qto_template.HasPropertyTemplates:
            if prop_template.Name != name:
                continue
            return prop_template.PrimaryMeasureType or "IfcLabel"
        return previous_value.is_a() if previous_value else "IfcLabel"
