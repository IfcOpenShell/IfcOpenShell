class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"style": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for key, value in self.settings["attributes"].items():
            if key == "SurfaceColour":
                self.edit_surface_colour(value)
            elif self.is_colour_or_factor(key):
                self.edit_colour_or_factor(key, value)
            else:
                setattr(self.settings["style"], key, value)

    def edit_surface_colour(self, value):
        self.settings["style"].SurfaceColour[1] = value[0]
        self.settings["style"].SurfaceColour[2] = value[1]
        self.settings["style"].SurfaceColour[3] = value[2]

    def is_colour_or_factor(self, name):
        return name in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]

    def edit_colour_or_factor(self, name, value):
        if isinstance(value, (list, tuple)):
            attribute = getattr(self.settings["style"], name)
            if not attribute or not attribute.is_a("IfcColourRgb"):
                colour = self.file.createIfcColourRgb(None, 0, 0, 0)
                setattr(self.settings["style"], name, colour)
                attribute = getattr(self.settings["style"], name)
            attribute[1] = value[0]
            attribute[2] = value[1]
            attribute[3] = value[2]
        else:
            existing_value = getattr(self.settings["style"], name)
            if existing_value and existing_value.id():
                self.file.remove(existing_value)
            setattr(self.settings["style"], name, self.file.createIfcNormalisedRatioMeasure(value))
