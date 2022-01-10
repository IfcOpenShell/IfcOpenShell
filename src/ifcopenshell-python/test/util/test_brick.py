import pytest
import test.bootstrap
import ifcopenshell.util.brick as subject


class TestGetBrickTypeIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        assert subject.get_brick_type(element) == "TerminalUnit"
        element.PredefinedType = "CONSTANTFLOW"
        assert subject.get_brick_type(element) == "CAV"
