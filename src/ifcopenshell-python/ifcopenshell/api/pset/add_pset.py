import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcObject"):
            for rel in self.settings["product"].IsDefinedBy or []:
                if (
                    rel.is_a("IfcRelDefinesByProperties")
                    and rel.RelatingPropertyDefinition.Name == self.settings["name"]
                ):
                    return rel.RelatingPropertyDefinition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": pset,
                }
            )
            return pset
        elif self.settings["product"].is_a("IfcTypeObject"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["name"]:
                    return definition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(pset)
            self.settings["product"].HasPropertySets = has_property_sets
            return pset
        elif self.settings["product"].is_a("IfcMaterialDefinition"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcMaterialProperties",
                **{
                    "Name": self.settings["name"],
                    "Material": self.settings["product"],
                }
            )
        elif self.settings["product"].is_a("IfcProfileDef"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcProfileProperties",
                **{
                    "Name": self.settings["name"],
                    "ProfileDefinition": self.settings["product"],
                }
            )
