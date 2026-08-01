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

import os
from collections import Counter

import numpy as np
import pytest
import shapely

import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.boundary as subject
import ifcopenshell.util.shape
import test.bootstrap


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


def _build_shapes_dict(ifc_file, elements):
    """Build a shapes dict as expected by ifcopenshell.util.boundary."""
    settings = ifcopenshell.geom.settings()
    settings.set("disable-opening-subtractions", True)
    shapes = {}
    for element in elements:
        shape = ifcopenshell.geom.create_shape(settings, element)
        shapes[element.id()] = {
            "verts": ifcopenshell.util.shape.get_vertices(shape.geometry),
            "faces": ifcopenshell.util.shape.get_faces(shape.geometry),
            "edges": ifcopenshell.util.shape.get_edges(shape.geometry),
            "matrix": ifcopenshell.util.shape.get_shape_matrix(shape),
        }
    return shapes


def _build_shapes_dict_from_iterator(ifc_file):
    """Build a shapes dict for all products in a file (excluding openings)."""
    settings = ifcopenshell.geom.settings()
    settings.set("disable-opening-subtractions", True)
    shapes = {}
    iterator = ifcopenshell.geom.iterator(settings, ifc_file)
    if iterator.initialize():
        while True:
            shape = iterator.get()
            element = ifc_file.by_id(shape.id)
            if not element.is_a("IfcOpeningElement"):
                shapes[shape.id] = {
                    "verts": ifcopenshell.util.shape.get_vertices(shape.geometry),
                    "faces": ifcopenshell.util.shape.get_faces(shape.geometry),
                    "edges": ifcopenshell.util.shape.get_edges(shape.geometry),
                    "matrix": ifcopenshell.util.shape.get_shape_matrix(shape),
                }
            if not iterator.next():
                break
    return shapes


def _boundaries_for(boundaries, element):
    return [b for b in boundaries if b.RelatedBuildingElement == element]


def _boundary_inner_count(boundary):
    surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement if boundary.ConnectionGeometry else None
    if surface and surface.is_a("IfcCurveBoundedPlane") and surface.InnerBoundaries:
        return len(surface.InnerBoundaries)
    return 0


def _outer_boundary_area(boundary):
    surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement
    points = [(p.Coordinates[0], p.Coordinates[1]) for p in surface.OuterBoundary.Points]
    area = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        area += x1 * y2 - x2 * y1
    return 0.5 * abs(area)


def _boundary_polygon_3d(boundary):
    """The boundary outer boundary as world-space 3D points."""
    surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement
    position = surface.BasisSurface.Position
    origin = np.array(position.Location.Coordinates, dtype=float)
    z = np.array(position.Axis.DirectionRatios if position.Axis else [0, 0, 1], dtype=float)
    x = np.array(position.RefDirection.DirectionRatios if position.RefDirection else [1, 0, 0], dtype=float)
    y = np.cross(z, x)
    points = np.array([[p.Coordinates[0], p.Coordinates[1]] for p in surface.OuterBoundary.Points])
    return origin + points[:, 0, None] * x + points[:, 1, None] * y


def _boundary_polygon_in_plane(boundary, reference=None):
    """The boundary polygon projected onto the reference boundary plane."""
    reference = reference or boundary
    surface = reference.ConnectionGeometry.SurfaceOnRelatingElement
    position = surface.BasisSurface.Position
    origin = np.array(position.Location.Coordinates, dtype=float)
    z = np.array(position.Axis.DirectionRatios if position.Axis else [0, 0, 1], dtype=float)
    x = np.array(position.RefDirection.DirectionRatios if position.RefDirection else [1, 0, 0], dtype=float)
    y = np.cross(z, x)
    points = _boundary_polygon_3d(boundary) - origin
    coords = [(float(p @ x), float(p @ y)) for p in points]
    return shapely.Polygon(coords)


def _add_wall_with_window(ifc_file):
    """Add a space bounded by a wall with a fully interior opening filled by a window."""
    space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace")
    wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
    opening_element = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcOpeningElement")
    window = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWindow")
    _add_extruded_body(ifc_file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
    _add_extruded_body(ifc_file, wall, [[-5, 5], [5, 5], [5, 5.5], [-5, 5.5]], 3.0)
    _add_extruded_body(ifc_file, opening_element, [[-2, 5], [2, 5], [2, 5.5], [-2, 5.5]], 1.8, z_offset=0.6)
    _add_extruded_body(ifc_file, window, [[-2, 4.5], [2, 4.5], [2, 5.5], [-2, 5.5]], 1.5, z_offset=0.75)
    ifc_file.createIfcRelVoidsElement(RelatingBuildingElement=wall, RelatedOpeningElement=opening_element)
    ifc_file.createIfcRelFillsElement(RelatingOpeningElement=opening_element, RelatedBuildingElement=window)
    return space, wall, window


def _add_roof_with_skylight(ifc_file):
    """Add a space with a roof pierced by an opening covered by a skylight window.

    The window is deliberately not related through IfcRelFillsElement to exercise
    the geometric detection of fillings.
    """
    space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace")
    roof = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcRoof")
    opening_element = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcOpeningElement")
    window = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWindow")
    _add_extruded_body(ifc_file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
    _add_extruded_body(ifc_file, roof, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 0.5, z_offset=3.0)
    _add_extruded_body(ifc_file, opening_element, [[-1, -1], [1, -1], [1, 1], [-1, 1]], 0.8, z_offset=2.8)
    _add_extruded_body(ifc_file, window, [[-1, -1], [1, -1], [1, 1], [-1, 1]], 0.2, z_offset=3.5)
    ifc_file.createIfcRelVoidsElement(RelatingBuildingElement=roof, RelatedOpeningElement=opening_element)
    return space, roof, window


def _external_earth_ifczip():
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "IfcRelSpaceBoundary_TestFiles",
        "IfcRelSpaceBoundary2ndLevel",
        "ExternalEarth_R20_IFC4.ifczip",
    )


def _boundary_element_counts(ifc_file, space_id):
    space = ifc_file.by_id(space_id)
    counts = Counter()
    for boundary in space.BoundedBy or []:
        if boundary.RelatedBuildingElement:
            counts[boundary.RelatedBuildingElement.id()] += 1
    return counts


class TestAutoGenerateBoundaries(test.bootstrap.IFC4):
    def test_no_building_elements_returns_error(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        _add_extruded_body(self.file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        shapes = _build_shapes_dict(self.file, [space])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary")
        assert isinstance(result, str)
        assert "No building elements" in result

    def test_space_not_in_shapes_returns_error(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        result = subject.auto_generate_boundaries(self.file, space, {}, "IfcRelSpaceBoundary")
        assert isinstance(result, str)
        assert "not found" in result.lower()

    def test_generates_boundary_for_adjacent_wall(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        _add_extruded_body(self.file, wall, [[-5, 5], [5, 5], [5, 5.2], [-5, 5.2]], 3.0)
        shapes = _build_shapes_dict(self.file, [space, wall])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary")
        assert isinstance(result, list)
        assert len(result) >= 1
        boundary = result[0]
        assert boundary.RelatingSpace == space
        assert boundary.RelatedBuildingElement == wall
        assert boundary.PhysicalOrVirtualBoundary == "PHYSICAL"

    def test_wall_boundary_with_window_has_no_inner_boundary(self):
        space, wall, window = _add_wall_with_window(self.file)
        shapes = _build_shapes_dict(self.file, [space, wall, window])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary2ndLevel")
        assert isinstance(result, list)
        wall_boundaries = _boundaries_for(result, wall)
        assert len(wall_boundaries) == 1
        assert _boundary_inner_count(wall_boundaries[0]) == 0
        assert _outer_boundary_area(wall_boundaries[0]) == pytest.approx(30.0, abs=1e-3)
        window_boundaries = _boundaries_for(result, window)
        assert len(window_boundaries) == 1
        assert window_boundaries[0].ParentBoundary == wall_boundaries[0]

    def test_roof_boundary_with_skylight_has_no_inner_boundary(self):
        space, roof, window = _add_roof_with_skylight(self.file)
        shapes = _build_shapes_dict(self.file, [space, roof, window])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary2ndLevel")
        assert isinstance(result, list)
        roof_boundaries = _boundaries_for(result, roof)
        assert len(roof_boundaries) == 1
        assert _boundary_inner_count(roof_boundaries[0]) == 0
        assert _outer_boundary_area(roof_boundaries[0]) == pytest.approx(100.0, abs=1e-3)
        window_boundaries = _boundaries_for(result, window)
        assert len(window_boundaries) == 1
        assert window_boundaries[0].ParentBoundary == roof_boundaries[0]

    def test_wall_boundary_with_unfilled_opening_has_no_inner_boundary(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        _add_extruded_body(self.file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        _add_extruded_body(self.file, wall, [[-5, 5], [5, 5], [5, 5.5], [-5, 5.5]], 3.0)
        _add_extruded_body(self.file, opening_element, [[-2, 5], [2, 5], [2, 5.5], [-2, 5.5]], 1.8, z_offset=0.6)
        self.file.createIfcRelVoidsElement(RelatingBuildingElement=wall, RelatedOpeningElement=opening_element)
        shapes = _build_shapes_dict(self.file, [space, wall])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary2ndLevel")
        assert isinstance(result, list)
        wall_boundaries = _boundaries_for(result, wall)
        assert len(wall_boundaries) == 1
        assert _boundary_inner_count(wall_boundaries[0]) == 0

    def test_openings_are_unioned_into_parent_boundary(self):
        # Some authoring tools bake the opening into the building element mesh,
        # leaving a notch in the gross boundary polygon. The parent boundary must
        # union the opening back in so it overlaps its own inner boundary.
        wall_face = shapely.Polygon([(-5, 5), (5, 5), (5, 5.5), (2, 5.5), (2, 5), (-2, 5), (-2, 5.5), (-5, 5.5)])
        window = shapely.Polygon([(-2, 5), (2, 5), (2, 5.5), (-2, 5.5)])
        assert wall_face.area == pytest.approx(3.0, abs=1e-9)
        parent = subject._union_openings_into_parent(wall_face, [("opening", "window", window)])
        assert isinstance(parent, shapely.Polygon)
        assert parent.area == pytest.approx(5.0, abs=1e-9)
        assert parent.contains(window)

    def test_external_earth_boundaries(self):
        ifczip = _external_earth_ifczip()
        if not os.path.exists(ifczip):
            pytest.skip("IfcRelSpaceBoundary_TestFiles submodule is not checked out")
        ifc_file = ifcopenshell.open(ifczip)
        shapes = _build_shapes_dict_from_iterator(ifc_file)
        for space_id, expected_counts in [
            (182, {996: 1, 1122: 1, 1235: 2, 1288: 1, 2970: 1, 3071: 1, 3140: 1, 3214: 1, 3435: 1, 3605: 1, 3719: 1}),
            (440, {1122: 1, 3140: 1, 3214: 1, 3493: 1, 3605: 1, 3640: 1, 3669: 1, 3719: 1}),
            (628, {3140: 1, 3838: 1, 3927: 1, 3980: 2, 4033: 1, 4086: 1, 4139: 1, 4199: 1}),
        ]:
            copy = ifcopenshell.file.from_string(ifc_file.wrapped_data.to_string())
            new_space = copy.by_id(space_id)
            result = subject.auto_generate_boundaries(
                copy, new_space, shapes=shapes, boundary_class="IfcRelSpaceBoundary2ndLevel"
            )
            assert _boundary_element_counts(copy, space_id) == expected_counts
            for boundary in result:
                assert _boundary_inner_count(boundary) == 0
                if boundary.ParentBoundary:
                    parent_polygon = _boundary_polygon_in_plane(boundary.ParentBoundary)
                    child_polygon = _boundary_polygon_in_plane(boundary, reference=boundary.ParentBoundary)
                    assert child_polygon.intersection(parent_polygon).area == pytest.approx(
                        child_polygon.area, abs=1e-2
                    )
            if space_id in (182, 440):
                roof_boundaries = _boundaries_for(result, copy.by_id(3214))
                assert len(roof_boundaries) == 1
                skylight = [b for b in result if b.RelatedBuildingElement.id() in (3435, 3640)]
                assert len(skylight) == 1
                assert skylight[0].ParentBoundary == roof_boundaries[0]
