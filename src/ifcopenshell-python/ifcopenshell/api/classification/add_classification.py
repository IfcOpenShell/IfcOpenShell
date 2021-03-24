import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.date

class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {
            "classification": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        edition_date = None
        if self.settings["classification"].EditionDate:
            edition_date = ifcopenshell.util.date.ifc2datetime(self.settings["classification"].EditionDate)
            self.settings["classification"].EditionDate = None

        migrator = ifcopenshell.util.schema.Migrator()
        result = migrator.migrate(self.settings["classification"], self.file)

        # TODO: should auto date migration be part of the migrator?
        if self.file.schema == "IFC2X3" and edition_date:
            result.EditionDate = ifcopenshell.util.date.datetime2ifc(edition_date, "IfcCalendarDate")
        else:
            result.EditionDate = ifcopenshell.util.date.datetime2ifc(edition_date, "IfcDate")

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
