class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"assigned_object": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.createIfcActorRole("ARCHITECT")
        roles = list(self.settings["assigned_object"].Roles) if self.settings["assigned_object"].Roles else []
        roles.append(element)
        self.settings["assigned_object"].Roles = roles
        return element
