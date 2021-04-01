class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"assigned_object": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        roles = list(self.settings["assigned_object"].Roles) if self.settings["assigned_object"].Roles else []
        roles.append(self.file.createIfcActorRole("ARCHITECT"))
        self.settings["assigned_object"].Roles = roles
