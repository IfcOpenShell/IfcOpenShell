import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "Name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcObject"):
            for rel in self.settings["product"].IsDefinedBy or []:
                if (
                    rel.is_a("IfcRelDefinesByProperties")
                    and rel.RelatingPropertyDefinition.Name == self.settings["Name"]
                ):
                    return rel.RelatingPropertyDefinition

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
            return pset
        elif self.settings["product"].is_a("IfcTypeObject"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["Name"]:
                    return definition

            pset = self.file.create_entity(
                "IfcPropertySet", **{"GlobalId": ifcopenshell.guid.new(), "Name": self.settings["Name"]}
            )
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(pset)
            self.settings["product"].HasPropertySets = has_property_sets
            return pset
        elif self.settings["product"].is_a("IfcMaterialDefinition"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["Name"]:
                    return definition

            return self.file.create_entity(
                "IfcMaterialProperties",
                **{
                    "Name": self.settings["Name"],
                    "Material": self.settings["product"],
                }
            )
