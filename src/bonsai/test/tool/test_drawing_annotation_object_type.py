# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import pytest

from bonsai.tool.drawing import Drawing as subject
from test.bim.bootstrap import NewFile


class TestSetupAnnotationObjectType(NewFile):
    @pytest.mark.parametrize("object_type", ["TEXT", "SYMBOL", "DIMENSION", "LINEWORK"])
    def test_ifc4x3_annotation_kind_is_stored_in_object_type(self, object_type):
        ifc = ifcopenshell.file(schema="IFC4X3")
        element = ifcopenshell.api.root.create_entity(ifc, "IfcAnnotation", predefined_type=object_type)
        subject.setup_annotation_object_type(element, object_type)
        assert element.ObjectType == object_type
        assert element.PredefinedType == "USERDEFINED"

    def test_ifc4_annotation_kind_is_stored_in_object_type(self):
        ifc = ifcopenshell.file(schema="IFC4")
        element = ifcopenshell.api.root.create_entity(ifc, "IfcAnnotation", predefined_type="TEXT")
        subject.setup_annotation_object_type(element, "TEXT")
        assert element.ObjectType == "TEXT"
