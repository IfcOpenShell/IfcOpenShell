class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"address": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["address"]):
            if inverse.is_a() in ("IfcOrganization", "IfcPerson"):
                if inverse.Addresses == (self.settings["address"],):
                    inverse.Addresses = None
        self.file.remove(self.settings["address"])
