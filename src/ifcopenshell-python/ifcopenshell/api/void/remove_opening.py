class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"opening": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        to_remove = [] # See bug #1224
        for rel in self.file.by_type("IfcRelVoidsElement"):
            if rel.RelatedOpeningElement == self.settings["opening"]:
                to_remove.append(rel)
                break
        for rel in self.file.by_type("IfcRelFillsElement"):
            if rel.RelatingOpeningElement == self.settings["opening"]:
                to_remove.append(rel)
                break
        self.file.remove(self.settings["opening"])
        for element in to_remove:
            self.file.remove(element)
