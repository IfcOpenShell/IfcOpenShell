import blenderbim.bim.schema  # TODO: refactor


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"pset": None, "Name": None, "Properties": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if hasattr(self.settings["pset"], "HasProperties"):
            attr_name = "HasProperties"
        elif hasattr(self.settings["pset"], "Properties"):  # For IfcMaterialProperties
            attr_name = "Properties"
        props = getattr(self.settings["pset"], attr_name) or []

        if self.settings["Name"]:
            self.settings["pset"].Name = self.settings["Name"]

        pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(self.settings["pset"].Name)

        for prop in props:
            if prop.Name in self.settings["Properties"]:
                value = self.settings["Properties"][prop.Name]
                primary_measure_type = self.get_primary_measure_type(
                    pset_template, prop.Name, previous_value=prop.NominalValue
                )
                if value is not None:
                    prop.NominalValue = self.file.create_entity(primary_measure_type, value)
                else:
                    prop.NominalValue = None
                del self.settings["Properties"][prop.Name]
        properties = []
        for name, value in self.settings["Properties"].items():
            if value is None:
                continue
            primary_measure_type = self.get_primary_measure_type(pset_template, name)
            properties.append(
                self.file.create_entity(
                    "IfcPropertySingleValue",
                    **{"Name": name, "NominalValue": self.file.create_entity(primary_measure_type, value)},
                )
            )
        props = list(props)
        props.extend(properties)
        setattr(self.settings["pset"], attr_name, props)

    def get_primary_measure_type(self, pset_template, name, previous_value=None):
        if not pset_template:
            return previous_value.is_a() if previous_value else "IfcLabel"
        for prop_template in pset_template.HasPropertyTemplates:
            if prop_template.Name == name:
                return prop_template.PrimaryMeasureType
        return previous_value.is_a() if previous_value else "IfcLabel"
