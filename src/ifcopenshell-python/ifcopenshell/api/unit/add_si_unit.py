class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit_type": "LENGTHUNIT", "name": "METRE", "prefix": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return self.file.create_entity(
            "IfcSIUnit", UnitType=self.settings["unit_type"], Name=self.settings["name"], Prefix=self.settings["prefix"]
        )
