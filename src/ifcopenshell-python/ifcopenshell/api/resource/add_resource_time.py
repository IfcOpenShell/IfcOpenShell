import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "resource": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        resource_time = self.file.create_entity("IfcResourceTime")
        self.settings["resource"].Usage = resource_time
        return resource_time
