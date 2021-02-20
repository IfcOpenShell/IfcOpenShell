class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "AxisTag": "A",
            "SameSense": True,
            "UVWAxes": "UAxes",  # Choose which axes
            "Grid": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.create_entity("IfcGridAxis", **{
            "AxisTag": self.settings["AxisTag"],
            "SameSense": self.settings["SameSense"]
        })
        axes = list(getattr(self.settings["Grid"], self.settings["UVWAxes"]) or [])
        axes.append(element)
        setattr(self.settings["Grid"], self.settings["UVWAxes"], axes)
        return element
