import ifcopenshell


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"opening": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.create_entity("IfcRelFillsElement", **{
            "GlobalId": ifcopenshell.guid.new(),
            "RelatingOpeningElement": self.settings["opening"],
            "RelatedBuildingElement": self.settings["element"]
        })
