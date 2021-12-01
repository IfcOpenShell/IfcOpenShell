import ifcopenshell
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"material": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["element"])
        if self.settings["material"].is_a("IfcMaterial"):
            ifcopenshell.api.run(
                "material.assign_material",
                self.file,
                product=self.settings["element"],
                type="IfcMaterial",
                material=self.settings["material"],
            )
        # No other material type can be copied right now.
        # 1. Material lists and constituents may have shape aspects and I
        # haven't implemented it yet.
        # 2. Material layer and profile sets implicitly define parametric
        # geometry and we have no way of guaranteeing that this constraint is
        # satisfied.
        # 3. Material set usages follow an unofficial constraint that all
        # instances must have a usage of their type's material set. We cannot
        # guarantee that constraint.
