import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


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
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_typed_by[0]})
            else:
                self.file.remove(is_typed_by[0])

        if types:
            related_objects = list(types[0].RelatedObjects)
            related_objects.append(self.settings["related_object"])
            types[0].RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": types[0]})
        else:
            types = self.file.create_entity(
                "IfcRelDefinesByType",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingType": self.settings["relating_type"],
                }
            )

        self.map_representations()
        self.map_material_usages()

    def map_representations(self):
        if not self.settings["relating_type"].RepresentationMaps:
            return
        representations = []
        if self.settings["related_object"].Representation:
            representations = self.settings["related_object"].Representation.Representations
        for representation in representations:
            # TODO: check if this is right? Surely this can be a single usecase?
            ifcopenshell.api.run(
                "geometry.unassign_representation",
                self.file,
                **{"product": self.settings["related_object"], "representation": representation}
            )
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        for representation_map in self.settings["relating_type"].RepresentationMaps:
            representation = representation_map.MappedRepresentation
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", self.file, **{"representation": representation}
            )
            ifcopenshell.api.run(
                "geometry.assign_representation",
                self.file,
                **{"product": self.settings["related_object"], "representation": mapped_representation}
            )

    def map_material_usages(self):
        type_material = ifcopenshell.util.element.get_material(self.settings["relating_type"])
        if not type_material:
            return
        if type_material.is_a("IfcMaterialLayerSet"):
            ifcopenshell.api.run(
                "material.assign_material",
                self.file,
                product=self.settings["related_object"],
                type="IfcMaterialLayerSetUsage",
            )
        elif type_material.is_a("IfcMaterialProfileSet"):
            ifcopenshell.api.run(
                "material.assign_material",
                self.file,
                product=self.settings["related_object"],
                type="IfcMaterialProfileSetUsage",
            )
