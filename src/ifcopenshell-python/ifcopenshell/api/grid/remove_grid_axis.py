import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"axis": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if len(self.file.get_inverse(self.settings["axis"].AxisCurve)) == 1:
            ifcopenshell.util.element.remove_deep(self.file, self.settings["axis"].AxisCurve)
            self.file.remove(self.settings["axis"].AxisCurve)
        self.file.remove(self.settings["axis"])
