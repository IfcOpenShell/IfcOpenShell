import ifcopenshell.util.schema


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"reference": None, "product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        total_related_objects = 0
        for association in self.file.by_type("IfcRelAssociatesClassification"):
            if association.RelatingClassification == self.settings["reference"] and association.RelatedObjects:
                total_related_objects += len(association.RelatedObjects)
                related_objects = list(association.RelatedObjects)
                try:
                    related_objects.remove(self.settings["product"])
                except:
                    continue
                if len(related_objects):
                    association.RelatedObjects = related_objects
                else:
                    self.file.remove(association)

        # TODO: we only handle lightweight classifications here
        if total_related_objects == 1:
            self.file.remove(self.settings["reference"])
