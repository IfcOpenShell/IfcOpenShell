import ifcopenshell
import blenderbim.bim.schema  # TODO: refactor


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "Name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcObject"):
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
