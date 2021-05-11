import ifcopenshell


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
        if self.settings["related_object"]:
            if self.file.schema == "IFC2X3":
                is_defined_by = self.settings["related_object"].IsDefinedBy
                for rel in is_defined_by:
                    if rel.is_a("IfcRelDefinesByType"):
                        return set([int(o.id()) for o in rel.RelatedObjects])
            else:
                is_typed_by = self.settings["related_object"].IsTypedBy
                if is_typed_by:
                    return set([int(o.id()) for o in is_typed_by[0].RelatedObjects])
        elif self.settings["relating_type"]:
            if self.file.schema == "IFC2X3":
                types = self.settings["relating_type"].ObjectTypeOf
            else:
                types = self.settings["relating_type"].Types
            if types:
                return set([int(o.id()) for o in types[0].RelatedObjects])
        return set()
