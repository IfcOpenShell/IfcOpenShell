import test.bootstrap
import ifcopenshell.api


class TestAddConversionBasedUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = ifcopenshell.api.run("unit.add_conversion_based_unit", self.file, name="foot")
        assert unit.is_a("IfcConversionBasedUnit")
        assert unit.Dimensions.LengthExponent == 1
        assert unit.Dimensions.MassExponent == 0
        assert unit.Dimensions.TimeExponent == 0
        assert unit.Dimensions.ElectricCurrentExponent == 0
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 0
        assert unit.Dimensions.AmountOfSubstanceExponent == 0
        assert unit.Dimensions.LuminousIntensityExponent == 0
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "foot"
        assert unit.ConversionFactor.ValueComponent.wrappedValue == 0.3048
        si_unit = unit.ConversionFactor.UnitComponent
        assert si_unit.is_a("IfcSIUnit")
        assert si_unit.UnitType == "LENGTHUNIT"
        assert si_unit.Prefix is None
        assert si_unit.Name == "METRE"

    def test_adding_a_unit_with_offset(self):
        unit = ifcopenshell.api.run("unit.add_conversion_based_unit", self.file, name="fahrenheit")
        assert unit.is_a("IfcConversionBasedUnitWithOffset")
        assert unit.Dimensions.LengthExponent == 0
        assert unit.Dimensions.MassExponent == 0
        assert unit.Dimensions.TimeExponent == 0
        assert unit.Dimensions.ElectricCurrentExponent == 0
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 1
        assert unit.Dimensions.AmountOfSubstanceExponent == 0
        assert unit.Dimensions.LuminousIntensityExponent == 0
        assert unit.UnitType == "THERMODYNAMICTEMPERATUREUNIT"
        assert unit.Name == "fahrenheit"
        assert unit.ConversionFactor.ValueComponent.wrappedValue == 1.8
        si_unit = unit.ConversionFactor.UnitComponent
        assert si_unit.is_a("IfcSIUnit")
        assert si_unit.UnitType == "THERMODYNAMICTEMPERATUREUNIT"
        assert si_unit.Prefix is None
        assert si_unit.Name == "KELVIN"
        assert unit.ConversionOffset == -459.67
