class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"classification": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        references = self.get_references(self.settings["classification"])
        for reference in references:
            self.file.remove(reference)
        self.file.remove(self.settings["classification"])
        for rel in self.file.by_type("IfcRelAssociatesClassification"):
            if not rel.RelatingClassification:
                self.file.remove(rel)

    def get_references(self, classification):
        results = []
        if not classification.HasReferences:
            return results
        for reference in classification.HasReferences:
            results.append(reference)
            results.extend(self.get_references(reference))
        return results
