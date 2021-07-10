class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "pset": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        to_purge = []
        should_remove_pset = True
        for inverse in self.file.get_inverse(self.settings["pset"]):
            if inverse.is_a("IfcRelDefinesByProperties"):
                if not inverse.RelatedObjects or len(inverse.RelatedObjects) == 1:
                    to_purge.append(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["product"])
                    inverse.RelatedObjects = related_objects
                    should_remove_pset = False
        if should_remove_pset:
            self.file.remove(self.settings["pset"])
        for element in to_purge:
            self.file.remove(element)
        # TODO: implement deep purging
