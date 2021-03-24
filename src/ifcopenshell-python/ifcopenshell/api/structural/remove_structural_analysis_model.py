class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"structural_analysis_model": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for rel in self.settings["structural_analysis_model"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["structural_analysis_model"])
