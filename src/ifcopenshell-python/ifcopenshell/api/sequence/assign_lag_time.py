class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"rel_sequence": None, "lag_value": None, "duration_type": "NOTEDEFINED"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        lag_value = self.file.createIfcDuration(self.settings["lag_value"])
        lag_time = self.file.create_entity("IfcLagTime",
            **{
            "DurationType": self.settings["duration_type"],
            "LagValue": lag_value,
            }
        )
        #Can an IfcLagTime entity be used by multiple sequence relationships?
        if self.settings["rel_sequence"].is_a("IfcRelSequence"):
            if len(self.file.get_inverse(self.settings["rel_sequence"].TimeLag)) == 1:
                self.file.remove(self.settings["rel_sequence"].TimeLag)
        self.settings["rel_sequence"].TimeLag = lag_time
