import pytest
import test.bootstrap
import ifcopenshell.util.brick as subject


class TestGetBrickTypeIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#TerminalUnit"
        element.PredefinedType = "CONSTANTFLOW"
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#CAV"


class TestGetBrickElementsIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        self.file.createIfcWall()
        assert subject.get_brick_elements(self.file) == [element]
