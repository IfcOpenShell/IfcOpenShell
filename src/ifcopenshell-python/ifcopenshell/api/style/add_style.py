class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # Name is filled out because Revit treats this incorrectly as the material name
        return self.file.createIfcSurfaceStyle(self.settings["name"], "BOTH")
