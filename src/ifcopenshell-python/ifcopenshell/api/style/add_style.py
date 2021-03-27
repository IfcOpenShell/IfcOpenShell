class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "Name": "Name",
            "SurfaceColour": [], # RGB
            "DiffuseColour": [], # RGB
            "Transparency": 0,
            "external_definition": {
                "Location": None,
                "Identification": None,
                "Name": "Name"
            },
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        styles = [self.create_surface_style_rendering()]
        if self.settings["external_definition"]:
            styles.append(self.create_externally_defined_surface_style())
        # Name is filled out because Revit treats this incorrectly as the material name
        return self.file.createIfcSurfaceStyle(self.settings["Name"], "BOTH", styles)

    def create_surface_style_rendering(self):
        return self.file.create_entity("IfcSurfaceStyleRendering", **{
            "SurfaceColour": self.create_colour_rgb(self.settings["SurfaceColour"]),
            "Transparency": (self.settings["Transparency"] - 1) * -1,
            "ReflectanceMethod": "NOTDEFINED",
            "DiffuseColour": self.create_colour_rgb(self.settings["DiffuseColour"])
        })

    def create_externally_defined_surface_style(self):
        self.file.create_entity(
            "IfcExternallyDefinedSurfaceStyle", **{
                "Location": self.settings["Location"],
                "Identification": self.settings["Identification"],
                "Name": self.settings["Name"],
            }
        )

    def create_colour_rgb(self, colour):
        return self.file.createIfcColourRgb(None, colour[0], colour[1], colour[2])
