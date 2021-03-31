class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_plan": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        if self.settings["work_plan"].HasContext:
            rel_declares = self.settings["work_plan"].HasContext[0]
            if len(rel_declares.RelatedDefinitions) == 1:
                self.file.remove(rel_declares)
        self.file.remove(self.settings["work_plan"])
