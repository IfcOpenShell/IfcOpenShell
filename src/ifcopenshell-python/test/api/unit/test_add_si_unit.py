import test.bootstrap
import ifcopenshell.api


class TestAddSIUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "METRE"
        assert unit.Prefix == "MILLI"
