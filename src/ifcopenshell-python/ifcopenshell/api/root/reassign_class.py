import ifcopenshell
import ifcopenshell.util.schema


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "ifc_class": "IfcBuildingElementProxy",
            "predefined_type": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = ifcopenshell.util.schema.reassign_class(
            self.file, self.settings["product"], self.settings["ifc_class"]
        )
        if self.settings["predefined_type"] and hasattr(element, "PredefinedType"):
            try:
                element.PredefinedType = self.settings["predefined_type"]
            except:
                element.PredefinedType = "USERDEFINED"
                element.ObjectType = self.settings["predefined_type"]
        return element
