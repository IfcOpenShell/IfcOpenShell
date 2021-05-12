import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file.create_entity("IfcPropertySetTemplate", **{
            "GlobalId": ifcopenshell.guid.new(),
            "Name": "New_Pset",
            "TemplateType": "PSET_TYPEDRIVENONLY",
            "ApplicableEntity": "IfcTypeObject"
        })
