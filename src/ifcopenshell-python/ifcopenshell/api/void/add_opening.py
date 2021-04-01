import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"opening": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.create_entity("IfcRelVoidsElement", **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
            "RelatingBuildingElement": self.settings["element"],
            "RelatedOpeningElement": self.settings["opening"]
        })
