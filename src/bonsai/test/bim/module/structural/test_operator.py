# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import pytest
from mathutils import Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestLoadBoundaryConditions(NewFile):
    def test_filtering_duplicate_names(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Pinned")
        props = tool.Structural.get_structural_props()
        props.filtered_boundary_conditions = True
        bpy.ops.bim.load_boundary_conditions()
        assert sorted(c.name for c in props.boundary_conditions) == ["Pinned"]


class TestEnableEditingStructuralItemAxis(NewFile):
    def test_starting_square_to_a_member_stood_up_along_its_axis(self):
        bpy.ops.bim.create_project()
        props = tool.Root.get_root_props()
        props.ifc_product, props.ifc_class, props.representation_template = (
            "IfcStructuralItem",
            "IfcStructuralCurveMember",
            "EDGE",
        )
        bpy.ops.bim.add_element(skip_dialog=True)
        member = tool.Ifc.get().by_type("IfcStructuralCurveMember")[0]
        obj = tool.Ifc.get_object(member)
        bpy.context.view_layer.objects.active = obj
        obj.data.vertices[1].co = obj.data.vertices[0].co + Vector((0.0, 0.0, 3.0))
        assert member.Axis.DirectionRatios == (0.0, 0.0, 1.0)  # Now parallel to the member.

        bpy.ops.bim.enable_editing_structural_item_axis()
        empty = tool.Structural.get_object_structural_props(obj).axis_empty
        x, y, z = (empty.matrix_world.col[i].to_3d() for i in range(3))
        assert abs(x.dot(Vector((0.0, 0.0, 1.0)))) == pytest.approx(1.0)
        assert y.length == pytest.approx(1.0)
        assert abs(z.dot(x)) < 1e-6

        bpy.ops.bim.edit_structural_item_axis()
        assert abs(Vector(member.Axis.DirectionRatios).normalized().z) < 1e-6
