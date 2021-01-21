import ifcopenshell
import ifcopenshell.util.schema

class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "classification": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        migrator = ifcopenshell.util.schema.Migrator()
        result = migrator.migrate(self.settings["classification"], self.file)
        self.file.create_entity("IfcRelAssociatesClassification", **{
            "GlobalId": ifcopenshell.guid.new(),
            "RelatedObjects": [self.file.by_type("IfcProject")[0]],
            "RelatingClassification": result
        })
        return # See bug #1272
        try:
            result = self.file.add(self.settings["classification"])
        except:
            migrator = ifcopenshell.util.schema.Migrator()
            result = migrator.migrate(self.settings["classification"], self.file)
