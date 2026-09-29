# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.root
from mathutils import Matrix

import bonsai.tool as tool
from bonsai.tool.loader import Loader as subject
from test.bim.bootstrap import NewFile


class TestCreateNativeSweptDiskSolid(NewFile):
    def test_item_with_only_a_curve_style_gets_no_material(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        subject.load_settings()
        points = [ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)), ifc.createIfcCartesianPoint((1.0, 0.0, 0.0))]
        solid = ifc.createIfcSweptDiskSolid(ifc.createIfcPolyline(points), 0.1)
        ifc.createIfcStyledItem(solid, [ifc.createIfcCurveStyle()])
        rep = ifc.createIfcShapeRepresentation(None, "Body", "AdvancedSweptSolid", [solid])
        element = ifcopenshell.api.root.create_entity(ifc, "IfcBuildingElementProxy")
        native_data = {"representation": rep, "matrix": Matrix()}
        curve, _ = subject.create_native_swept_disk_solid(element, "Curve", native_data)
        assert list(curve.materials) == [None]
