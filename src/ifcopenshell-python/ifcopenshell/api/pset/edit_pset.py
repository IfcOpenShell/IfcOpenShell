import blenderbim.bim.schema  # TODO: refactor


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"pset": None, "Name": None, "Properties": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.update_pset_name()
        self.load_pset_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_pset_with_new_properties(new_properties)

    def update_pset_name(self):
        if self.settings["Name"]:
            self.settings["pset"].Name = self.settings["Name"]

    def load_pset_template(self):
        self.pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(self.settings["pset"].Name)

    def update_existing_properties(self):
        for prop in self.get_properties():
            self.update_existing_property(prop)

    def update_existing_property(self, prop):
        if prop.Name not in self.settings["Properties"]:
            return
        value = self.settings["Properties"][prop.Name]
        if value is None:
            prop.NominalValue = None
        else:
            primary_measure_type = self.get_primary_measure_type(prop.Name, previous_value=prop.NominalValue)
            prop.NominalValue = self.file.create_entity(primary_measure_type, value)
        del self.settings["Properties"][prop.Name]

    def add_new_properties(self):
        properties = []
        for name, value in self.settings["Properties"].items():
            if value is None:
                continue
            primary_measure_type = self.get_primary_measure_type(name)
            properties.append(
                self.file.create_entity(
                    "IfcPropertySingleValue",
                    **{"Name": name, "NominalValue": self.file.create_entity(primary_measure_type, value)},
                )
            )
        return properties

    def extend_pset_with_new_properties(self, new_properties):
        props = list(self.get_properties())
        props.extend(new_properties)
        if hasattr(self.settings["pset"], "HasProperties"):
            self.settings["pset"].HasProperties = props
        elif hasattr(self.settings["pset"], "Properties"):
            self.settings["pset"].Properties = props

    def get_properties(self):
        if hasattr(self.settings["pset"], "HasProperties"):
            return self.settings["pset"].HasProperties or []
        elif hasattr(self.settings["pset"], "Properties"):  # For IfcMaterialProperties
            return self.settings["pset"].Properties or []

    def get_primary_measure_type(self, name, previous_value=None):
        if not self.pset_template:
            return previous_value.is_a() if previous_value else "IfcLabel"
        for prop_template in self.pset_template.HasPropertyTemplates:
            if prop_template.Name != name:
                continue
            return prop_template.PrimaryMeasureType or "IfcLabel"
        return previous_value.is_a() if previous_value else "IfcLabel"
