import test.bootstrap
import ifcopenshell.api


class TestAddContextDependentUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = ifcopenshell.api.run(
            "unit.add_context_dependent_unit",
            self.file,
            unit_type="LENGTHUNIT",
            name="foobar",
            dimensions=(1, 2, 3, 4, 5, 6, 7),
        )
        assert unit.is_a("IfcContextDependentUnit")
        assert unit.Dimensions.LengthExponent == 1
        assert unit.Dimensions.MassExponent == 2
        assert unit.Dimensions.TimeExponent == 3
        assert unit.Dimensions.ElectricCurrentExponent == 4
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 5
        assert unit.Dimensions.AmountOfSubstanceExponent == 6
        assert unit.Dimensions.LuminousIntensityExponent == 7
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "foobar"
