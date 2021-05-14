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

            qto = self.file.create_entity(
                "IfcElementQuantity", **{"GlobalId": ifcopenshell.guid.new(), "Name": self.settings["Name"]}
            )
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    # TODO: owner history
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": qto,
                }
            )
            return qto
