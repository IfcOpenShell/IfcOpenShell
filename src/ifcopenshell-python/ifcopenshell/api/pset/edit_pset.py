import ifcopenshell
import ifcopenshell.util.pset


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"pset": None, "name": None, "properties": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.update_pset_name()
        self.load_pset_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_pset_with_new_properties(new_properties)

    def update_pset_name(self):
        if self.settings["name"]:
            self.settings["pset"].Name = self.settings["name"]

    def load_pset_template(self):
        # TODO: add IFC2X3 PsetQto template support
        self.psetqto = ifcopenshell.util.pset.get_template("IFC4")
        self.pset_template = self.psetqto.get_by_name(self.settings["pset"].Name)

    def update_existing_properties(self):
        for prop in self.get_properties():
            self.update_existing_property(prop)

    def update_existing_property(self, prop):
        if prop.Name not in self.settings["properties"]:
            return
        value = self.settings["properties"][prop.Name]
        if value is None:
            prop.NominalValue = None
        else:
            primary_measure_type = self.get_primary_measure_type(prop.Name, previous_value=prop.NominalValue)
            prop.NominalValue = self.file.create_entity(primary_measure_type, value)
        del self.settings["properties"][prop.Name]

    def add_new_properties(self):
        properties = []
        for name, value in self.settings["properties"].items():
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
