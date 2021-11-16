class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"reference": None, "product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        rels = self.settings["reference"].LibraryRefForObjects
        if not rels:
            return
        for rel in rels:
            if self.settings["product"] in rel.RelatedObjects:
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    continue
                related_objects = list(rel.RelatedObjects)
                related_objects.remove(self.settings["product"])
                rel.RelatedObjects = related_objects
