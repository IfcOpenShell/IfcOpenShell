import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "Name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcObject"):
            pset = self.file.create_entity(
                "IfcPropertySet", **{"GlobalId": ifcopenshell.guid.new(), "Name": self.settings["Name"]}
            )
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    # TODO: owner history
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": pset,
                }
            )
        elif self.settings["product"].is_a("IfcTypeObject"):
            pset = self.file.create_entity(
                "IfcPropertySet", **{"GlobalId": ifcopenshell.guid.new(), "Name": self.settings["Name"]}
            )
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(pset)
            self.settings["product"].HasPropertySets = has_property_sets
        elif self.settings["product"].is_a("IfcMaterialDefinition"):
            pset = self.file.create_entity(
                "IfcMaterialProperties",
                **{
                    "Name": self.settings["Name"],
                    "Material": self.settings["product"],
                }
            )
