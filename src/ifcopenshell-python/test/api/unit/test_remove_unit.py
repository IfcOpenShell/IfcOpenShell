import test.bootstrap
import ifcopenshell.api


class TestRemoveUnit(test.bootstrap.IFC4):
    def test_remove_a_single_unit(self):
        unit = self.file.createIfcContextDependentUnit()
        ifcopenshell.api.run("unit.remove_unit", self.file, unit=unit)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0

    def test_remove_the_only_assigned_unit(self):
        self.file.createIfcProject()
        unit = self.file.createIfcContextDependentUnit()
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])
        ifcopenshell.api.run("unit.remove_unit", self.file, unit=unit)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0
        assert len(self.file.by_type("IfcUnitAssignment")) == 0

    def test_remove_an_assigned_unit(self):
        self.file.createIfcProject()
        unit1 = self.file.createIfcContextDependentUnit()
        unit2 = self.file.createIfcSIUnit()
        assignment = ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit1, unit2])
        ifcopenshell.api.run("unit.remove_unit", self.file, unit=unit1)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0
        assert assignment.Units == (unit2,)

    def test_removing_a_unit_deeply(self):
        unit = ifcopenshell.api.run("unit.add_conversion_based_unit", self.file, name="foot")
        ifcopenshell.api.run("unit.remove_unit", self.file, unit=unit)
        assert len([e for e in self.file]) == 0
