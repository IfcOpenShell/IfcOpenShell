# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from bonsai.tool.drawing import Drawing as subject
from test.bim.bootstrap import NewFile


class TestGetCameraRepresentation(NewFile):
    def create_drawing(self, identifier):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC4"))
        drawing = ifcopenshell.api.root.create_entity(ifc, "IfcAnnotation", name="Drawing")
        context = ifc.createIfcGeometricRepresentationContext(None, "Model")
        representation = ifc.createIfcShapeRepresentation(context, identifier, "SweptSolid", [])
        drawing.Representation = ifc.createIfcProductDefinitionShape(None, None, [representation])
        return drawing, representation

    def test_falls_back_to_a_body_representation_in_another_context(self):
        drawing, representation = self.create_drawing("Body")
        assert subject.get_camera_representation(drawing) == representation

    def test_an_annotation_representation_is_not_a_camera(self):
        drawing, _ = self.create_drawing("Annotation")
        with pytest.raises(ValueError, match="no camera representation"):
            subject.get_camera_representation(drawing)

    def test_importing_a_drawing_without_a_camera_raises_a_value_error(self):
        drawing, _ = self.create_drawing("Annotation")
        with pytest.raises(ValueError, match="no camera representation"):
            subject.import_drawing(drawing)
