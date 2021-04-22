class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material_profile": None, "profile": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if (
            self.settings["material_profile"].Profile
            and len(self.file.get_inverse(self.settings["material_profile"].Profile)) == 1
        ):
            self.file.remove(self.settings["material_profile"].Profile)
        self.settings["material_profile"].Profile = self.settings["profile"]
