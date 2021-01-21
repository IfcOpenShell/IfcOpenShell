import ifcopenshell


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"product": None, "type": "IfcMaterial", "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["type"] == "IfcMaterial":
            self.assign_ifc_material()
        elif self.settings["type"] == "IfcMaterialConstituentSet":
            material_set = self.file.create_entity(self.settings["type"])
            material_set.MaterialConstituents = [self.settings["material"]]
            self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialLayerSet":
            material_set = self.file.create_entity(self.settings["type"])
            material_set.MaterialLayers = [self.settings["material"]]
            self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialProfileSet":
            material_set = self.file.create_entity(self.settings["type"])
            material_set.MaterialProfiles = [self.settings["material"]]
            self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialList":
            material_set = self.file.create_entity(self.settings["type"])
            material_set.Materials = [self.settings["material"]]
            self.create_material_association(material_set)

    def assign_ifc_material(self):
        rel = self.get_rel_associates_material(self.settings["material"])
        if not rel:
            return self.create_material_association(self.settings["material"])
        related_objects = list(rel.RelatedObjects)
        related_objects.append(self.settings["product"])
        rel.RelatedObjects = related_objects

    def create_material_association(self, relating_material):
        return self.file.create_entity(
            "IfcRelAssociatesMaterial",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatedObjects": [self.settings["product"]],
                "RelatingMaterial": relating_material,
            }
        )

    def get_rel_associates_material(self, material):
        if self.file.schema == "IFC2X3":
            rel = [
                r
                for r in self.file.by_type("IfcRelAssociatesMaterial")
                if r.RelatingMaterial == self.settings["material"]
            ]
            return rel[0] if rel else None
        if self.settings["material"].AssociatedTo:
            return self.settings["material"].AssociatedTo[0]
