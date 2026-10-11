# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.geometry

POINTS = [(1.0, 1.0, 1.0), (3.0, 1.0, 1.0), (3.0, 2.0, 1.0), (1.0, 2.0, 1.5)]
MOVED_POINTS = [(1.0, 1.0, 1.0), (3.0, 1.0, 4.0), (3.0, 2.0, 1.0), (1.0, 2.0, 1.5)]
RADIUS = 0.025
SCHEMAS = ("IFC4", "IFC2X3")


def create_curve_object(spline_type: str, closed: bool) -> bpy.types.Object:
    curve = bpy.data.curves.new("Curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = RADIUS
    spline = curve.splines.new(spline_type)
    if spline_type == "BEZIER":
        spline.bezier_points.add(len(POINTS) - 1)
        for point, co in zip(spline.bezier_points, POINTS):
            point.co = co
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    else:
        spline.points.add(len(POINTS) - 1)
        for point, co in zip(spline.points, POINTS):
            point.co = (*co, 1.0)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new("Curve", curve)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_file(schema: str) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    ifc = ifcopenshell.api.project.create_file(version=schema)
    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc, length={"is_metric": True, "raw": "MILLIMETERS"})
    model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    return ifc, body


def scale_points(points: list[tuple[float, ...]], scale: float) -> list[tuple[float, ...]]:
    return [tuple(round(co * scale, 3) for co in point) for point in points]


def get_path_edges(points: list[tuple[float, ...]], closed: bool, scale: float) -> set[frozenset]:
    points = scale_points(points, scale)
    if closed:
        points.append(points[0])
    return {frozenset(edge) for edge in zip(points, points[1:])}


def get_directrix_points(item: ifcopenshell.entity_instance) -> list[tuple[float, ...]]:
    directrix = item.Directrix
    if directrix.is_a("IfcPolyline"):
        points = [point.Coordinates for point in directrix.Points]
    else:
        points = directrix.Points.CoordList
        if directrix.Segments:
            points = [points[index - 1] for segment in directrix.Segments for index in segment[0]]
    return scale_points(points, 1.0)


def get_directrix_edges(item: ifcopenshell.entity_instance) -> set[frozenset]:
    points = get_directrix_points(item)
    return {frozenset(edge) for edge in zip(points, points[1:])}


def get_body_items(element: ifcopenshell.entity_instance) -> tuple[ifcopenshell.entity_instance, ...]:
    body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    return body.Items


def move_point(curve: bpy.types.Curve, old: tuple[float, ...], new: tuple[float, ...]) -> None:
    points = [point for spline in curve.splines for point in spline.points if tuple(point.co[:3]) == old]
    assert len(points) == 1
    points[0].co = (*new, 1.0)


class TestAddSweptDiskRepresentation(NewFile):
    @pytest.mark.parametrize("schema", SCHEMAS)
    @pytest.mark.parametrize("closed", (False, True))
    def test_a_beveled_poly_curve_becomes_one_swept_disk_along_its_points(self, schema, closed):
        ifc, body = create_file(schema)
        tool.Ifc.set(ifc)
        obj = create_curve_object("POLY", closed)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc, context=body, blender_object=obj, geometry=obj.data
        )
        assert representation.RepresentationType == "AdvancedSweptSolid"
        assert [item.is_a() for item in representation.Items] == ["IfcSweptDiskSolid"]
        item = representation.Items[0]
        assert item.Radius == pytest.approx(RADIUS * 1000)
        assert get_directrix_edges(item) == get_path_edges(POINTS, closed, scale=1000)
        assert obj.data.bevel_depth == pytest.approx(RADIUS)
        assert list(bpy.data.objects) == [obj]

    @pytest.mark.parametrize("schema", SCHEMAS)
    def test_a_beveled_bezier_curve_becomes_one_swept_disk_through_its_control_points(self, schema):
        ifc, body = create_file(schema)
        tool.Ifc.set(ifc)
        obj = create_curve_object("BEZIER", closed=False)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc, context=body, blender_object=obj, geometry=obj.data
        )
        assert [item.is_a() for item in representation.Items] == ["IfcSweptDiskSolid"]
        item = representation.Items[0]
        assert item.Radius == pytest.approx(RADIUS * 1000)
        control_points = scale_points(POINTS, 1000)
        directrix_points = get_directrix_points(item)
        assert {directrix_points[0], directrix_points[-1]} == {control_points[0], control_points[-1]}
        assert set(control_points) < set(directrix_points)


class TestAssignClassToBeveledCurve(NewFile):
    @pytest.mark.parametrize("schema", SCHEMAS)
    @pytest.mark.parametrize("closed", (False, True))
    def test_a_beveled_poly_curve_becomes_a_swept_disk_curve(self, schema, closed):
        tool.Project.get_project_props().export_schema = schema
        bpy.ops.bim.create_project()
        tool.Loader.load_settings()
        obj = create_curve_object("POLY", closed)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcFlowSegment")
        scale = 1 / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        items = get_body_items(tool.Ifc.get_entity(obj))
        assert [item.is_a() for item in items] == ["IfcSweptDiskSolid"]
        assert items[0].Radius == pytest.approx(RADIUS * scale)
        assert get_directrix_edges(items[0]) == get_path_edges(POINTS, closed, scale=scale)
        assert isinstance(obj.data, bpy.types.Curve)
        assert obj.data.bevel_depth == pytest.approx(RADIUS)


class TestUpdateSweptDiskRepresentation(NewFile):
    def load_swept_disk(
        self, tmp_path, schema: str, closed: bool
    ) -> tuple[ifcopenshell.entity_instance, bpy.types.Object]:
        ifc, body = create_file(schema)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcFlowSegment")
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc)
        directrix = builder.polyline(scale_points(POINTS, 1000), closed=closed)
        item = ifc.createIfcSweptDiskSolid(directrix, RADIUS * 1000)
        representation = ifc.createIfcShapeRepresentation(body, "Body", "AdvancedSweptSolid", [item])
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(ifc, product=element)
        filepath = str(tmp_path / "swept_disk.ifc")
        ifc.write(filepath)
        bpy.ops.bim.load_project(filepath=filepath)
        element = tool.Ifc.get().by_type("IfcFlowSegment")[0]
        obj = tool.Ifc.get_object(element)
        assert isinstance(obj.data, bpy.types.Curve)
        return element, obj

    @pytest.mark.parametrize("schema", SCHEMAS)
    @pytest.mark.parametrize("closed", (False, True))
    def test_moving_a_curve_point_moves_the_directrix(self, tmp_path, schema, closed):
        element, obj = self.load_swept_disk(tmp_path, schema, closed)
        move_point(obj.data, POINTS[1], MOVED_POINTS[1])
        bpy.ops.bim.update_representation(obj=obj.name)
        items = get_body_items(element)
        assert [item.is_a() for item in items] == ["IfcSweptDiskSolid"]
        assert items[0].Radius == pytest.approx(RADIUS * 1000)
        assert get_directrix_edges(items[0]) == get_path_edges(MOVED_POINTS, closed, scale=1000)

    def test_moving_a_curve_point_in_edit_mode_moves_the_directrix(self, tmp_path):
        element, obj = self.load_swept_disk(tmp_path, "IFC4", closed=False)
        tool.Blender.select_and_activate_single_object(bpy.context, obj)
        bpy.ops.object.mode_set(mode="EDIT")
        move_point(obj.data, POINTS[1], MOVED_POINTS[1])
        bpy.ops.bim.update_representation(obj=obj.name)
        items = get_body_items(element)
        assert [item.is_a() for item in items] == ["IfcSweptDiskSolid"]
        assert get_directrix_edges(items[0]) == get_path_edges(MOVED_POINTS, closed=False, scale=1000)

    @pytest.mark.parametrize("schema", SCHEMAS)
    def test_changing_the_bevel_depth_changes_the_radius(self, tmp_path, schema):
        element, obj = self.load_swept_disk(tmp_path, schema, closed=False)
        obj.data.bevel_depth = 0.05
        bpy.ops.bim.update_representation(obj=obj.name)
        items = get_body_items(element)
        assert [item.is_a() for item in items] == ["IfcSweptDiskSolid"]
        assert items[0].Radius == pytest.approx(50.0)
        assert get_directrix_edges(items[0]) == get_path_edges(POINTS, closed=False, scale=1000)

    @pytest.mark.parametrize("schema", SCHEMAS)
    def test_a_curve_material_becomes_the_style_of_the_swept_disk(self, tmp_path, schema):
        element, obj = self.load_swept_disk(tmp_path, schema, closed=False)
        material = bpy.data.materials.new("Material")
        obj.data.materials.append(material)
        bpy.ops.bim.update_representation(obj=obj.name)
        items = get_body_items(element)
        assert [item.is_a() for item in items] == ["IfcSweptDiskSolid"]
        style = tool.Ifc.get_entity(material)
        assert style.is_a("IfcSurfaceStyle")
        assert tool.Style.get_representation_item_style(items[0]) == style
