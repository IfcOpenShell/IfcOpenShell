class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"profile_set": None, "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        profiles = list(self.settings["profile_set"].MaterialProfiles or [])
        profile = self.file.create_entity("IfcMaterialProfile", **{"Material": self.settings["material"]})
        profiles.append(profile)
        self.settings["profile_set"].MaterialProfiles = profiles
        return profile
