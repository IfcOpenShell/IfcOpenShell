import ifcopenshell.util.unit
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        unit_assignment = ifcopenshell.util.unit.get_unit_assignment(self.file)
        if unit_assignment and self.settings["unit"] in unit_assignment.Units:
            units = list(unit_assignment.Units)
            units.remove(self.settings["unit"])
            if units:
                unit_assignment.Units = units
            else:
                self.file.remove(unit_assignment)
        ifcopenshell.util.element.remove_deep(self.file, self.settings["unit"])
