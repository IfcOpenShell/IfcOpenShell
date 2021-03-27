import ifcopenshell
import ifcopenshell.api.owner.create_owner_history as create_owner_history
import ifcopenshell.api.owner.update_owner_history as update_owner_history


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None,
            "relating_type": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.schema == "IFC2X3":
            is_typed_by = None
            is_defined_by = self.settings["related_object"].IsDefinedBy
            for rel in is_defined_by:
                if rel.is_a("IfcRelDefinesByType"):
                    is_typed_by = [rel]
                    break
            types = self.settings["relating_type"].ObjectTypeOf
        else:
            is_typed_by = self.settings["related_object"].IsTypedBy
            types = self.settings["relating_type"].Types

        if types and is_typed_by == types:
            return

        if is_typed_by:
            related_objects = list(is_typed_by[0].RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                is_typed_by[0].RelatedObjects = related_objects
                update_owner_history.Usecase(self.file, {"element": is_typed_by[0]}).execute()
            else:
                self.file.remove(is_typed_by[0])

        if types:
            related_objects = list(types[0].RelatedObjects)
            related_objects.append(self.settings["related_object"])
            types[0].RelatedObjects = related_objects
            update_owner_history.Usecase(self.file, {"element": types[0]}).execute()
        else:
            types = self.file.create_entity(
                "IfcRelDefinesByType",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": create_owner_history.Usecase(self.file).execute(),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingType": self.settings["relating_type"],
                }
            )
