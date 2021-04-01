import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.schema == "IFC2X3":
            is_typed_by = None
            is_defined_by = self.settings["related_object"].IsDefinedBy
            for rel in is_defined_by:
                if rel.is_a("IfcRelDefinesByType"):
                    is_typed_by = rel
        else:
            is_typed_by = self.settings["related_object"].IsTypedBy
            if is_typed_by:
                is_typed_by = is_typed_by[0]

        if is_typed_by:
            related_objects = list(is_typed_by.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                is_typed_by.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_typed_by})
            else:
                self.file.remove(is_typed_by)
