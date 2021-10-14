import test.bootstrap
import ifcopenshell.api


class TestAddMonetaryUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = ifcopenshell.api.run("unit.add_monetary_unit", self.file, currency="USD")
        assert unit.is_a("IfcMonetaryUnit")
        assert unit.Currency == "USD"
