import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.brick as subject


class TestGetBrickTypeIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#TerminalUnit"
        element.PredefinedType = "CONSTANTFLOW"
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#CAV"
        element = self.file.createIfcEngine()
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#Equipment"


class TestGetBrickTypeIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowController")
        type_element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcAirTerminalBoxType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=type_element)
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#TerminalUnit"


class TestGetBrickElementsIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        self.file.createIfcWall()
        assert subject.get_brick_elements(self.file) == {element}
