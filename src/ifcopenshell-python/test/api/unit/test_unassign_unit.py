import test.bootstrap
import ifcopenshell.api


class TestUnassignUnit(test.bootstrap.IFC4):
    def test_run(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="FOO")
        unit2 = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="BAR")
        assignment = ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit1, unit2])
        ifcopenshell.api.run("unit.unassign_unit", self.file, units=[unit1])
        assert unit1 not in assignment.Units
        assert unit2 in assignment.Units

    def test_unassigning_the_last_unit(self):
        project = self.file.createIfcProject()
        unit = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="FOO")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])
        ifcopenshell.api.run("unit.unassign_unit", self.file, units=[unit])
        assert project.UnitsInContext is None

    def test_doing_nothing_if_the_unit_is_not_assigned(self):
        unit = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="FOO")
        assert ifcopenshell.api.run("unit.unassign_unit", self.file, units=[unit]) is None
