class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"structural_member": None, "axis": [0.0, 0.0, 1.0]}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.get_inverse(self.settings["structural_member"].Axis) == 1:
            self.file.remove(self.settings["structural_member"].Axis)
        self.settings["structural_member"].Axis = self.file.createIfcDirection(self.settings["axis"])
