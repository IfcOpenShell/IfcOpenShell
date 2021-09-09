class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "axis_tag": "A",
            "same_sense": True,
            "uvw_axes": "UAxes",  # Choose which axes
            "grid": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.create_entity(
            "IfcGridAxis", **{"axis_tag": self.settings["axis_tag"], "SameSense": self.settings["same_sense"]}
        )
        axes = list(getattr(self.settings["grid"], self.settings["uvw_axes"]) or [])
        axes.append(element)
        setattr(self.settings["grid"], self.settings["uvw_axes"], axes)
        return element
