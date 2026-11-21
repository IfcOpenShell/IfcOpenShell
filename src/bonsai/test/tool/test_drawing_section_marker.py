# This file was generated with the assistance of an AI coding tool.

from math import pi

import bpy
import ifcopenshell.api.geometry
import ifcopenshell.util.representation
import pytest
from ifcopenshell.util.shape_builder import ShapeBuilder
from mathutils import Matrix, Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def add_plan_and_section(location_hint, is_flipped):
    bpy.ops.bim.create_project()
    tool.Project.save_test_project()
    bpy.ops.bim.load_drawings()
    bpy.ops.bim.add_drawing()
    props = tool.Drawing.get_document_props()
    props.target_view = "SECTION_VIEW"
    props.location_hint = location_hint
    bpy.ops.bim.add_drawing()
    ifc = tool.Ifc.get()
    plan = next(d for d in ifc.by_type("IfcAnnotation") if tool.Drawing.get_drawing_target_view(d) == "PLAN_VIEW")
    section = next(d for d in ifc.by_type("IfcAnnotation") if tool.Drawing.get_drawing_target_view(d) == "SECTION_VIEW")
    if is_flipped:
        obj = tool.Ifc.get_object(section)
        obj.matrix_world = Matrix.Rotation(pi, 4, "X") @ obj.matrix_world
        tool.Geometry.run_edit_object_placement(obj)
    return plan, section


def marker_is_on_view_side(plan, section, points):
    plan_matrix = tool.Ifc.get_object(plan).matrix_world
    section_matrix = tool.Ifc.get_object(section).matrix_world
    view_dir = plan_matrix.inverted().to_3x3() @ (section_matrix.to_3x3() @ Vector((0, 0, -1)))
    edge = Vector(points[1]) - Vector(points[0])
    return edge.x * view_dir.y - edge.y * view_dir.x > 0


class TestSectionReferenceAnnotation(NewFile):
    @pytest.mark.parametrize("is_flipped", [False, True])
    @pytest.mark.parametrize("location_hint", ["NORTH", "SOUTH", "EAST", "WEST"])
    def test_marker_side_faces_the_view_direction(self, location_hint, is_flipped):
        plan, section = add_plan_and_section(location_hint, is_flipped)
        assert marker_is_on_view_side(plan, section, tool.Drawing.generate_section_reference_points(plan, section))

    @pytest.mark.parametrize("location_hint", ["NORTH", "SOUTH"])
    def test_regenerating_reorients_a_reversed_annotation(self, location_hint):
        plan, section = add_plan_and_section(location_hint, False)
        context = tool.Drawing.get_annotation_context("PLAN_VIEW")
        annotation = tool.Drawing.generate_reference_annotation(plan, section, context)
        tool.Geometry.run_edit_object_placement(tool.Ifc.get_object(annotation))
        old = ifcopenshell.util.representation.get_representation(annotation, context)
        reversed_points = list(reversed(old.Items[0].Points.CoordList))
        ifcopenshell.api.geometry.unassign_representation(tool.Ifc.get(), product=annotation, representation=old)
        builder = ShapeBuilder(tool.Ifc.get())
        representation = builder.get_representation(context, [builder.polyline(reversed_points)])
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), annotation, representation)

        tool.Drawing.regenerate_reference_annotation(plan, annotation, section, context)

        new = ifcopenshell.util.representation.get_representation(annotation, context)
        assert marker_is_on_view_side(plan, section, new.Items[0].Points.CoordList)
