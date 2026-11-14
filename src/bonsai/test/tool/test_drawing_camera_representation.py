# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.geometry
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
        with pytest.raises(subject.CameraGeometryError, match="no camera representation"):
            subject.get_camera_representation(drawing)

    def test_importing_a_drawing_without_a_camera_raises_a_camera_geometry_error(self):
        drawing, _ = self.create_drawing("Annotation")
        with pytest.raises(subject.CameraGeometryError, match="no camera representation"):
            subject.import_drawing(drawing)


class TestActivateDrawingWithoutCamera(NewFile):
    def create_drawing_without_camera(self):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        ifc = tool.Ifc.get()
        drawing = ifc.by_type("IfcAnnotation")[0]
        camera = tool.Ifc.get_object(drawing)
        bpy.data.objects.remove(camera)
        ifcopenshell.api.geometry.unassign_representation(
            ifc, product=drawing, representation=tool.Drawing.get_camera_representation(drawing)
        )
        return drawing

    @pytest.mark.parametrize("use_quick_preview", [False, True])
    def test_the_operator_reports_an_error_instead_of_a_traceback(self, use_quick_preview):
        drawing = self.create_drawing_without_camera()
        with pytest.raises(RuntimeError) as e:
            bpy.ops.bim.activate_drawing(drawing=drawing.id(), use_quick_preview=use_quick_preview)
        assert "no camera representation" in str(e.value)
        assert "Traceback" not in str(e.value)
