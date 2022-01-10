import test.bootstrap
import ifcopenshell.api


class TestEditMonetaryUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = self.file.createIfcMonetaryUnit()
        ifcopenshell.api.run("unit.edit_monetary_unit", self.file, unit=unit, attributes={"Currency": "FOO"})
        assert unit.Currency == "FOO"
