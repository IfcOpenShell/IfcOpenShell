# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape
import ifcopenshell.util.space as subject
import pytest
import shapely
import test.bootstrap


def _build_shapes_dict(ifc_file, elements):
    """Build a shapes dict as expected by ifcopenshell.util.space functions."""
    settings = ifcopenshell.geom.settings()
    settings.set("disable-opening-subtractions", True)
    settings.set("use-world-coords", True)
    shapes = {}
    for element in elements:
        shape = ifcopenshell.geom.create_shape(settings, element)
        verts = ifcopenshell.util.shape.get_shape_vertices(shape, shape.geometry)
        faces = ifcopenshell.util.shape.get_faces(shape.geometry)
        zs = verts[:, 2]
        shapes[element.id()] = {
            "verts": verts,
            "faces": faces,
            "bottom_z": float(zs.min()),
            "top_z": float(zs.max()),
        }
    return shapes


def _add_extruded_body(ifc_file, element, coords_2d, depth, z_offset=0.0):
    """Add a body representation (extruded polyline) to an element."""
    if not ifc_file.by_type("IfcProject"):
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    ctx = ifc_file.createIfcGeometricRepresentationContext(
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-5,
        WorldCoordinateSystem=ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
            ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
        ),
    )
    sub_ctx = ifc_file.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=ctx,
        TargetView="MODEL_VIEW",
    )
    pts = [ifc_file.createIfcCartesianPoint((float(x), float(y))) for x, y in coords_2d]
    polyline = ifc_file.createIfcPolyline(pts)
    profile = ifc_file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="CURVE", OuterCurve=polyline)
    placement = ifc_file.createIfcAxis2Placement3D(
        ifc_file.createIfcCartesianPoint((0.0, 0.0, z_offset)),
        ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
        ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
    )
    direction = ifc_file.createIfcDirection((0.0, 0.0, 1.0))
    solid = ifc_file.createIfcExtrudedAreaSolid(profile, placement, direction, depth)
    rep = ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=sub_ctx,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=rep)


class TestGetBoundaryLines(test.bootstrap.IFC4):
    def test_returns_segments_for_intersecting_walls(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, wall, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        shapes = _build_shapes_dict(self.file, [wall])
        lines, bounding = subject.get_boundary_lines(self.file, shapes, cut_z=1.0)
        assert len(lines) > 0
        assert wall in bounding

    def test_skips_elements_not_intersecting_plane(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, wall, [[-1, -1], [1, -1], [1, 1], [-1, 1]], 1.0)
        shapes = _build_shapes_dict(self.file, [wall])
        lines, bounding = subject.get_boundary_lines(self.file, shapes, cut_z=10.0)
        assert lines == []
        assert bounding == []

    def test_skips_non_bounding_classes(self):
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        _add_extruded_body(self.file, slab, [[-1, -1], [1, -1], [1, 1], [-1, 1]], 1.0)
        shapes = _build_shapes_dict(self.file, [slab])
        lines, bounding = subject.get_boundary_lines(self.file, shapes, cut_z=0.5)
        assert slab not in bounding


class TestGetSpacePolygon(test.bootstrap.IFC4):
    def test_finds_containing_polygon(self):
        lines = [
            shapely.LineString([(0, 0), (10, 0)]),
            shapely.LineString([(10, 0), (10, 10)]),
            shapely.LineString([(10, 10), (0, 10)]),
            shapely.LineString([(0, 10), (0, 0)]),
        ]
        polygon, _ = subject.get_space_polygon(lines, 5, 5)
        assert not isinstance(polygon, str)
        assert polygon.area == pytest.approx(100)

    def test_no_polygons_found(self):
        polygon, _ = subject.get_space_polygon([], 0, 0)
        assert polygon == "NO POLYGONS FOUND"

    def test_no_polygon_for_point(self):
        lines = [
            shapely.LineString([(0, 0), (10, 0)]),
            shapely.LineString([(10, 0), (10, 10)]),
            shapely.LineString([(10, 10), (0, 10)]),
            shapely.LineString([(0, 10), (0, 0)]),
        ]
        polygon, _ = subject.get_space_polygon(lines, 50, 50)
        assert polygon == "NO POLYGON FOR POINT"


class TestGetAutoSpaceHeight(test.bootstrap.IFC4):
    def test_height_from_top_connection(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        _add_extruded_body(self.file, wall, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        _add_extruded_body(self.file, slab, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 0.3, z_offset=3.0)
        self.file.createIfcRelConnectsElements(
            GlobalId=ifcopenshell.guid.new(),
            RelatingElement=slab,
            RelatedElement=wall,
            Description="TOP",
        )
        shapes = _build_shapes_dict(self.file, [wall, slab])
        space_polygon = shapely.box(-5, -5, 5, 5)
        height = subject.get_auto_space_height(self.file, shapes, space_polygon, 0.0, [wall])
        assert height is not None
        assert height == pytest.approx(3.0, abs=0.1)

    def test_height_from_elements_above_without_top_connection(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        _add_extruded_body(self.file, wall, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        _add_extruded_body(self.file, slab, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 0.3, z_offset=3.0)
        shapes = _build_shapes_dict(self.file, [wall, slab])
        space_polygon = shapely.box(-5, -5, 5, 5)
        height = subject.get_auto_space_height(self.file, shapes, space_polygon, 0.0, [wall])
        assert height is not None
        assert height == pytest.approx(3.0, abs=0.1)

    def test_height_from_wall_tops_when_no_slab(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, wall, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        shapes = _build_shapes_dict(self.file, [wall])
        space_polygon = shapely.box(-5, -5, 5, 5)
        height = subject.get_auto_space_height(self.file, shapes, space_polygon, 0.0, [wall])
        assert height is not None
        assert height == pytest.approx(3.0, abs=0.1)

    def test_returns_none_when_no_elements_above(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, wall, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        shapes = _build_shapes_dict(self.file, [wall])
        space_polygon = shapely.box(-100, -100, -90, -90)
        height = subject.get_auto_space_height(self.file, shapes, space_polygon, 0.0, [])
        assert height is None
