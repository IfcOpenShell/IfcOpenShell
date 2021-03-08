import ifcopenshell
from blenderbim.bim.module.owner.api import create_owner_history


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity("IfcGroup", **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": create_owner_history(),
            "Name": "Unnamed"
        })
