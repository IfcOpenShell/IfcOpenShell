import test.bootstrap
from typing import cast
import ifcopenshell
from ifcopenshell.file_IFC4 import _file as _file_IFC4
from ifcopenshell.api.multischema import SchemaAttrParser, AstAnnotationUnion, AstAnnotationType


class TestCreateEntity(test.bootstrap.IFC4):
    def test_create_entity(self):
        self.file = cast(_file_IFC4, self.file)
        wall = self.file.root.create_entity(ifc_class="IfcWall", name="My Wall")
        assert wall.is_a() == "IfcWall"
        assert wall.Name == "My Wall"


class TestParseIfcSimpleType(test.bootstrap.IFC4):
    def test_parse_ifc_simple_type(self):
        self.file = cast(_file_IFC4, self.file)
        args = SchemaAttrParser(ifc_class="IfcDerivedUnitElement")()
        exponent = [arg for arg in args if arg.name == "exponent"][0]
        assert exponent.name == "exponent"
        assert (
            isinstance(exponent.annotation, AstAnnotationUnion)
            and any([
                isinstance(a, AstAnnotationType)
                and a.annotation_type is int
                for a in exponent.annotation.annotations
            ])
        )
