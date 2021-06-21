import ifcopenshell.util.representation


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material_profile": None, "profile": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: handle composite profiles
        old_profile = self.settings["material_profile"].Profile
        self.settings["material_profile"].Profile = self.settings["profile"]
        for profile_set in self.settings["material_profile"].ToMaterialProfileSet:
            for inverse in self.file.get_inverse(profile_set):
                if not inverse.is_a("IfcMaterialProfileSetUsage"):
                    continue
                if self.file.schema == "IFC2X3":
                    for rel in self.file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        for element in rel.RelatedObjects:
                            self.change_profile(element)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_profile(element)

        if old_profile and len(self.file.get_inverse(old_profile)) == 0:
            self.file.remove(old_profile)

    def change_profile(self, element):
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return
        for subelement in self.file.traverse(representation):
            if subelement.is_a("IfcSweptAreaSolid"):
                subelement.SweptArea = self.settings["profile"]
