class Data:
    is_loaded = False
    profiles = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.profiles = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.profiles = {}
        for profile in file.by_type("IfcProfileDef"):
            cls.profiles[profile.id()] = profile.get_info()
        cls.is_loaded = True
