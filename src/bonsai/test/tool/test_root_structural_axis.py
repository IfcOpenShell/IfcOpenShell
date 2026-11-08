# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestSetDefaultStructuralAxis(NewFile):
    def create(self, ifc_class, end):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC4"))
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class)
        mesh = bpy.data.meshes.new("Mesh")
        mesh.from_pydata([(0, 0, 0), end], [(0, 1)], [])
        return ifc, element, bpy.data.objects.new("Obj", mesh)

    @pytest.mark.parametrize(
        "ifc_class, end, expected",
        [
            ("IfcStructuralCurveMember", (3, 0, 0), (0.0, 0.0, 1.0)),
            ("IfcStructuralCurveMember", (0, 0, 3), (1.0, 0.0, 0.0)),
            ("IfcStructuralCurveConnection", (3, 0, 0), (0.0, 0.0, 1.0)),
        ],
    )
    def test_a_missing_axis_is_set_to_a_direction_not_parallel_to_the_curve(self, ifc_class, end, expected):
        _, element, obj = self.create(ifc_class, end)
        tool.Root.set_default_structural_axis(element, obj)
        assert element.Axis.DirectionRatios == expected

    def test_an_existing_axis_is_kept(self):
        ifc, element, obj = self.create("IfcStructuralCurveMember", (3, 0, 0))
        element.Axis = ifc.createIfcDirection((0.0, 1.0, 0.0))
        tool.Root.set_default_structural_axis(element, obj)
        assert element.Axis.DirectionRatios == (0.0, 1.0, 0.0)

    def test_other_classes_are_ignored(self):
        _, element, obj = self.create("IfcWall", (3, 0, 0))
        tool.Root.set_default_structural_axis(element, obj)
        assert not element.is_a("IfcStructuralCurveMember")
