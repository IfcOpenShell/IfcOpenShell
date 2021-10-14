class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"units": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        unit_assignment = self.file.by_type("IfcUnitAssignment")
        if not unit_assignment:
            return
        unit_assignment = unit_assignment[0]
        units = set(unit_assignment.Units or [])
        units = units - set(self.settings["units"])
        if units:
            unit_assignment.Units = list(units)
            return unit_assignment
        self.file.remove(unit_assignment)
