class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit_type": "USERDEFINED", "name": "THINGAMAJIG", "dimensions": (0, 0, 0, 0, 0, 0, 0)}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity(
            "IfcContextDependentUnit",
            Dimensions=self.file.createIfcDimensionalExponents(*self.settings["dimensions"]),
            UnitType=self.settings["unit_type"],
            Name=self.settings["name"],
        )
