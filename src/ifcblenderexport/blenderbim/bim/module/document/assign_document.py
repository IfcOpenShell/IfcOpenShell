import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "document": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        rel = self.get_document_rel()
        related_objects = set(rel.RelatedObjects) if rel.RelatedObjects else set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)

    def get_document_rel(self):
        rel = None
        if self.file.schema == "IFC2X3":
            for association in self.file.by_type("IfcRelAssociatesDocument"):
                if association.RelatingDocument == self.settings["document"]:
                    return rel
        else:
            if (
                hasattr(self.settings["document"], "DocumentRefForObjects")
                and self.settings["document"].DocumentRefForObjects
            ):
                return self.settings["document"].DocumentRefForObjects[0]
            elif (
                hasattr(self.settings["document"], "DocumentInfoForObjects")
                and self.settings["document"].DocumentInfoForObjects
            ):
                return self.settings["document"].DocumentInfoForObjects[0]

        return self.file.create_entity("IfcRelAssociatesDocument", **{
            "GlobalId": ifcopenshell.guid.new(),
            # TODO: owner history
            "RelatingDocument": self.settings["document"]
        })
