import ifcopenshell
import ifcopenshell.api.owner.create_owner_history as create_owner_history


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"opening": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.create_entity("IfcRelVoidsElement", **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": create_owner_history.Usecase(self.file).execute(),
            "RelatingBuildingElement": self.settings["element"],
            "RelatedOpeningElement": self.settings["opening"]
        })
