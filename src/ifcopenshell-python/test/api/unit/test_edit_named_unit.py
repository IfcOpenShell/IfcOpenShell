import test.bootstrap
import ifcopenshell.api


class TestEditNamedUnit(test.bootstrap.IFC4):
    def test_edit_context_dependent_unit(self):
        unit = self.file.createIfcContextDependentUnit()
        unit.Dimensions = self.file.createIfcDimensionalExponents()
        ifcopenshell.api.run(
            "unit.edit_named_unit",
            self.file,
            unit=unit,
            attributes={"Dimensions": (1, 2, 3, 4, 5, 6, 7), "UnitType": "LENGTHUNIT", "Name": "Name"},
        )
        assert [a for a in unit.Dimensions] == [1, 2, 3, 4, 5, 6, 7]
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "Name"

    def test_edit_si_unit(self):
        unit = self.file.createIfcSIUnit()
        ifcopenshell.api.run(
            "unit.edit_named_unit",
            self.file,
            unit=unit,
            attributes={"UnitType": "LENGTHUNIT", "Prefix": "MILLI", "Name": "METRE"},
        )
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Prefix == "MILLI"
        assert unit.Name == "METRE"

    def test_edit_conversion_based_unit(self):
        unit = self.file.createIfcConversionBasedUnit()
        unit.Dimensions = self.file.createIfcDimensionalExponents()
        ifcopenshell.api.run(
            "unit.edit_named_unit",
            self.file,
            unit=unit,
            attributes={"Dimensions": (1, 2, 3, 4, 5, 6, 7), "UnitType": "LENGTHUNIT", "Name": "Name"},
        )
        assert [a for a in unit.Dimensions] == [1, 2, 3, 4, 5, 6, 7]
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "Name"

    def test_edit_conversion_based_unit_with_offset(self):
        unit = self.file.createIfcConversionBasedUnitWithOffset()
        unit.Dimensions = self.file.createIfcDimensionalExponents()
        ifcopenshell.api.run(
            "unit.edit_named_unit",
            self.file,
            unit=unit,
            attributes={
                "Dimensions": (1, 2, 3, 4, 5, 6, 7),
                "UnitType": "LENGTHUNIT",
                "Name": "Name",
                "ConversionOffset": 1,
            },
        )
        assert [a for a in unit.Dimensions] == [1, 2, 3, 4, 5, 6, 7]
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "Name"
        assert unit.ConversionOffset == 1
