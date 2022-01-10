import test.bootstrap
import ifcopenshell.api


class TestEditDerivedUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = self.file.createIfcDerivedUnit()
        ifcopenshell.api.run(
            "unit.edit_derived_unit",
            self.file,
            unit=unit,
            attributes={"UnitType": "USERDEFINED", "UserDefinedType": "UserDefinedType"},
        )
        assert unit.UnitType == "USERDEFINED"
        assert unit.UserDefinedType == "UserDefinedType"
