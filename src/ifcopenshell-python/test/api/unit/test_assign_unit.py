import test.bootstrap
import ifcopenshell.api


class TestAssignUnit(test.bootstrap.IFC4):
    def test_run(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="FOO")
        unit2 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="BAR")
        assignment = ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit1, unit2])
        assert project.UnitsInContext == assignment
        assert assignment.is_a("IfcUnitAssignment")
        assert unit1 in assignment.Units
        assert unit2 in assignment.Units

    def test_assign_units_to_an_existing_assignment(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="FOO")
        unit2 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="BAR")
        assignment1 = ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit1])
        assignment2 = ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit2])
        assert project.UnitsInContext == assignment1
        assert assignment1 == assignment2
        assert unit1 in assignment1.Units
        assert unit2 in assignment1.Units
