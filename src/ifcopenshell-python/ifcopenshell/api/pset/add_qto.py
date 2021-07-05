import ifcopenshell
import ifcopenshell.api


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

            qto = self.file.create_entity(
                "IfcElementQuantity",
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
                    "RelatingPropertyDefinition": qto,
                }
            )
            return qto
