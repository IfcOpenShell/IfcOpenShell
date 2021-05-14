class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"connection": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["connection"].AppliedCondition:
            return
        if len(self.file.get_inverse(self.settings["connection"].AppliedCondition)) == 1:
            self.file.remove(self.settings["connection"].AppliedCondition)
        self.settings["connection"].AppliedCondition = None
