# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.shape_builder import ShapeBuilder

import bonsai.tool as tool
from bonsai.tool.loader import Loader as subject
from test.bim.bootstrap import NewFile


class TestConvertGeometryToMesh(NewFile):
    def test_representation_mixing_polygons_and_curves_keeps_both(self):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC4"))
        builder = ShapeBuilder(ifc)
        fill_area = ifc.createIfcAnnotationFillArea(builder.polyline([(0, 0), (1, 0), (1, 1), (0, 1)], closed=True))
        curve_set = ifc.createIfcGeometricCurveSet([builder.polyline([(2, 0), (3, 0)])])
        context = ifc.createIfcGeometricRepresentationContext()
        rep = ifc.createIfcShapeRepresentation(context, "Annotation", "Annotation2D", [fill_area, curve_set])
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, rep)
        mesh = subject.convert_geometry_to_mesh(shape, bpy.data.meshes.new("Mesh"))
        assert len(mesh.polygons) > 0
        assert len([e for e in mesh.edges if e.is_loose]) == 1
