import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"relation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["relation"].AppliedCondition:
            ifcopenshell.api.run(
                "structural.remove_structural_boundary_condition",
                self.file,
                **{"connection": self.settings["relation"].RelatedStructuralConnection}
            )
        self.file.remove(self.settings["relation"])

