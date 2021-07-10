import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "ifc_class": "IfcStructuralPlanarAction",
            "predefined_type": "CONST",
            "global_or_local": "GLOBAL_COORDS",
            "applied_load": None,
            "structural_member": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        activity = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class=self.settings["ifc_class"],
            predefined_type=self.settings["predefined_type"],
        )
        activity.AppliedLoad = self.settings["applied_load"]
        activity.GlobalOrLocal = self.settings["global_or_local"]

        rel = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelConnectsStructuralActivity")
        rel.RelatingElement = self.settings["structural_member"]
        rel.RelatedStructuralActivity = activity
        return activity
