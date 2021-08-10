import ifcopenshell.util.element


class Usecase():
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        unit_assignment = self.file.by_type("IfcUnitAssignment")[0]
        units = list(unit_assignment.Units)
        units.remove(self.settings["unit"])
        if not units:
            return
        unit_assignment.Units = units
        ifcopenshell.util.element.remove_deep(self.file, self.settings["unit"])
