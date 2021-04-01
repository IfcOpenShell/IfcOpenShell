import ifcopenshell

class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        id_attribute = "ItemReference" if self.file.schema == "IFC2X3" else "Identification"
        return self.file.create_entity("IfcDocumentReference", **{
            id_attribute: ifcopenshell.guid.new()
        })
