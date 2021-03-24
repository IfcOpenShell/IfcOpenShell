class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "style": None,
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
        #has_external_definition = None
        for element in self.file.traverse(self.settings["style"]):
            if element.is_a("IfcSurfaceStyleShading"):
                if element.SurfaceColour:
                    self.update_colour_rgb(element.SurfaceColour, self.settings["SurfaceColour"])
                else:
                    element.SurfaceColour = self.create_colour_rgb(self.settings["SurfaceColour"])
                element.Transparency = (self.settings["Transparency"] - 1) * -1
            if element.is_a("IfcSurfaceStyleRendering"):
                if element.DiffuseColour:
                    self.update_colour_rgb(element.DiffuseColour, self.settings["DiffuseColour"])
                else:
                    element.DiffuseColour = self.create_colour_rgb(self.settings["DiffuseColour"])
            # TODO: Move to separate usecase
            #if element.is_a("IfcExternallyDefinedSurfaceStyle"):
            #    element.Location = self.settings["Location"]
            #    element.Identification = self.settings["Identification"]
            #    element.Name = self.settings["Name"]
            #    has_external_definition = True
        #if not has_external_definition:
        #    styles = list(self.settings["style"].Styles)
        #    styles.append(self.create_externally_defined_surface_style())
        #    self.settings["style"].Styles = styles
        return self.settings["style"]

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

    def update_colour_rgb(self, element, colour):
        element[1] = colour[0]
        element[2] = colour[1]
        element[3] = colour[2]
