import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.pset
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        unit = {"is_metric": "METERS" in self.args[0], "raw": self.args[0]}
        self.file_patched = ifcopenshell.api.run("project.create_file", version=self.file.schema)
        project = ifcopenshell.api.run("root.create_entity", self.file_patched, ifc_class="IfcProject")
        unit_assignment = ifcopenshell.api.run("unit.assign_unit", self.file_patched, **{"length": unit})

        # Is there a better way?
        for element in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            element.Precision = 1E-8

        # If we don't add openings first, they don't get converted
        for element in self.file.by_type("IfcOpeningElement"):
            self.file_patched.add(element)

        for element in self.file:
            self.file_patched.add(element)

        new_length = [u for u in unit_assignment.Units if u.UnitType == "LENGTHUNIT"][0]
        old_length = [
            u for u in self.file_patched.by_type("IfcProject")[1].UnitsInContext.Units if u.UnitType == "LENGTHUNIT"
        ][0]

        for inverse in self.file_patched.get_inverse(old_length):
            ifcopenshell.util.element.replace_attribute(inverse, old_length, new_length)

        self.file_patched.remove(old_length)
        self.file_patched.remove(project)
