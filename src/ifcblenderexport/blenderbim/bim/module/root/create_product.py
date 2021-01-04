import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "ifc_class": "IfcBuildingElementProxy",
            "predefined_type": None,
            "name": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.create_entity(self.settings["ifc_class"], **{"GlobalId": ifcopenshell.guid.new()})
        element.Name = self.settings["name"] or None
        if self.settings["predefined_type"] and hasattr(element, "PredefinedType"):
            try:
                element.PredefinedType = self.settings["predefined_type"]
            except:
                element.PredefinedType = "USERDEFINED"
                element.ObjectType = self.settings["predefined_type"]
        return element
