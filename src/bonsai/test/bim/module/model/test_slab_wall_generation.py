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

"""Coverage for ``DumbWallGenerator``'s slab-to-wall perimeter extraction
(``Shift+A -> Add From Perimeter``), in particular the profile shapes that
used to raise or produce wrong geometry:

- ``IfcCircleProfileDef`` / ``IfcRectangleProfileDef`` (and their hollow
  variants): these have no ``OuterCurve`` attribute at all, so the
  ``profile.OuterCurve`` access previously crashed with ``AttributeError``
  the same way ``IfcCompositeProfileDef`` did before that was fixed.
- ``IfcIndexedPolyCurve`` arc segments: previously treated as straight
  chords through raw ``CoordList`` order.
- ``IfcArbitraryProfileDefWithVoids``: inner curves (holes) are now turned
  into their own ring of walls, wound opposite the outer boundary.

Tests exercise the helper methods directly with real ``ifcopenshell``
entities (built via a throwaway ``ifcopenshell.file()``) and plain
``mathutils.Matrix``/``Mock`` objects -- these helpers never touch
Blender's RNA/registered-class layer."""

import math
from unittest.mock import Mock, patch

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.bim.module.model.wall import DumbWallGenerator

pytestmark = pytest.mark.model


def make_generator(unit_scale: float = 1.0) -> DumbWallGenerator:
    """A ``DumbWallGenerator`` with just ``unit_scale`` set, bypassing
    ``__init__``'s dependency on a live IFC file / relating type -- the
    methods under test only read ``self.unit_scale``."""
    generator = object.__new__(DumbWallGenerator)
    generator.unit_scale = unit_scale
    return generator


def make_slab_obj(matrix_world: Matrix = None) -> Mock:
    slab_obj = Mock()
    slab_obj.matrix_world = matrix_world if matrix_world is not None else Matrix.Identity(4)
    return slab_obj


def polyline_points_from_walls(loop_walls) -> list[Vector]:
    """Reconstruct the ordered point loop from the ``coords`` recorded on
    each wall dict: point0->point1, point1->point2, ..."""
    points = [loop_walls[0]["coords"][0]]
    for wall in loop_walls:
        points.append(wall["coords"][1])
    return points


# ---------------------------------------------------------------------------
# _curve_has_arc_segments
# ---------------------------------------------------------------------------


def test_curve_has_arc_segments_true_for_arc_index():
    ifc_file = ifcopenshell.file()
    points = ifc_file.createIfcCartesianPointList2D(CoordList=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
    segments = [ifc_file.createIfcArcIndex((1, 2, 3))]
    curve = ifc_file.createIfcIndexedPolyCurve(Points=points, Segments=segments)

    assert make_generator()._curve_has_arc_segments(curve) is True


def test_curve_has_arc_segments_false_for_line_index_only():
    ifc_file = ifcopenshell.file()
    points = ifc_file.createIfcCartesianPointList2D(CoordList=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
    segments = [ifc_file.createIfcLineIndex((1, 2)), ifc_file.createIfcLineIndex((2, 3))]
    curve = ifc_file.createIfcIndexedPolyCurve(Points=points, Segments=segments)

    assert make_generator()._curve_has_arc_segments(curve) is False


def test_curve_has_arc_segments_false_for_non_indexed_poly_curve():
    ifc_file = ifcopenshell.file()
    curve = ifc_file.createIfcCircle(Radius=1.0)

    assert make_generator()._curve_has_arc_segments(curve) is False


# ---------------------------------------------------------------------------
# _resolution_for_radius / _estimate_arc_segment_count -- arc/circle sample
# count scales with physical size so small fillets don't explode into many
# tiny wall segments, while large arcs stay capped at SLAB_ARC_RESOLUTION.
# ---------------------------------------------------------------------------


def test_resolution_for_radius_clamps_small_fillet_to_minimum():
    generator = make_generator()
    # A 5cm fillet is well under one SLAB_ARC_SEGMENT_LENGTH (10cm) of arc length.
    assert generator._resolution_for_radius(0.05) == generator.SLAB_MIN_ARC_SEGMENTS


def test_resolution_for_radius_caps_large_radius_at_max():
    generator = make_generator()
    assert generator._resolution_for_radius(1.0) == generator.SLAB_ARC_RESOLUTION


def test_resolution_for_radius_scales_between_bounds():
    generator = make_generator()
    resolution = generator._resolution_for_radius(0.2)
    assert generator.SLAB_MIN_ARC_SEGMENTS < resolution < generator.SLAB_ARC_RESOLUTION


def test_resolution_for_radius_handles_zero_or_negative():
    generator = make_generator()
    assert generator._resolution_for_radius(0.0) == generator.SLAB_MIN_ARC_SEGMENTS
    assert generator._resolution_for_radius(-1.0) == generator.SLAB_MIN_ARC_SEGMENTS


def test_estimate_arc_segment_count_matches_known_radius():
    generator = make_generator()
    # Quarter circle of radius 1 centred on the origin: (1,0) -> (cos45,sin45) -> (0,1).
    p1 = Vector((1.0, 0.0, 0.0))
    p2 = Vector((math.cos(math.radians(45)), math.sin(math.radians(45)), 0.0))
    p3 = Vector((0.0, 1.0, 0.0))

    assert generator._estimate_arc_segment_count(p1, p2, p3) == generator._resolution_for_radius(1.0)


def test_estimate_arc_segment_count_handles_collinear_points():
    """Three collinear points are a degenerate 'arc' (zero-area triangle);
    the circumradius formula would divide by zero, so this must fall back
    to a safe minimum rather than raising or returning nonsense."""
    generator = make_generator()
    p1 = Vector((0.0, 0.0, 0.0))
    p2 = Vector((1.0, 0.0, 0.0))
    p3 = Vector((2.0, 0.0, 0.0))

    assert generator._estimate_arc_segment_count(p1, p2, p3) == generator.SLAB_MIN_ARC_SEGMENTS


# ---------------------------------------------------------------------------
# _derive_points_from_circle -- also used directly for IfcCircleProfileDef
# ---------------------------------------------------------------------------


def test_derive_points_from_circle_samples_expected_radius():
    ifc_file = ifcopenshell.file()
    circle = ifc_file.createIfcCircle(Radius=2.0)
    generator = make_generator()

    points = generator._derive_points_from_circle(Matrix.Identity(4), elevation=3.0, circle=circle)

    assert points[0] == points[-1]  # explicitly closed loop
    assert len(points) - 1 == generator._resolution_for_radius(2.0)
    assert all(p.z == 3.0 for p in points)
    # theta=0 sample sits exactly on +X at the given radius.
    assert points[0].x == pytest.approx(2.0)
    assert points[0].y == pytest.approx(0.0)


def test_derive_points_from_circle_radius_override_for_hollow_inner_loop():
    ifc_file = ifcopenshell.file()
    circle = ifc_file.createIfcCircle(Radius=2.0)
    generator = make_generator()

    points = generator._derive_points_from_circle(Matrix.Identity(4), elevation=0.0, circle=circle, radius_override=1.5)

    assert points[0].x == pytest.approx(1.5)


def test_derive_points_from_circle_applies_unit_scale():
    ifc_file = ifcopenshell.file()
    circle = ifc_file.createIfcCircle(Radius=1000.0)  # e.g. millimetres
    generator = make_generator(unit_scale=0.001)  # project length unit is mm

    points = generator._derive_points_from_circle(Matrix.Identity(4), elevation=0.0, circle=circle)

    assert points[0].x == pytest.approx(1.0)  # scaled down to metres


def test_derive_points_from_circle_applies_world_matrix():
    """world_matrix carries both the object's own transform and the
    IfcExtrudedAreaSolid's Position -- a plain translation here stands in
    for either (or their combination)."""
    ifc_file = ifcopenshell.file()
    circle = ifc_file.createIfcCircle(Radius=2.0)
    generator = make_generator()
    world_matrix = Matrix.Translation(Vector((10.0, 5.0, 0.0)))

    points = generator._derive_points_from_circle(world_matrix, elevation=0.0, circle=circle)

    assert points[0].x == pytest.approx(12.0)
    assert points[0].y == pytest.approx(5.0)


def test_derive_points_from_circle_handles_profile_with_real_ref_direction():
    """Regression test: unlike IfcRectangleProfileDef (whose Position is
    always None from the profile-fitting operator), IfcCircleProfileDef.Position
    is always a real IfcAxis2Placement2D with an explicit RefDirection -- this
    used to raise ValueError from ifcopenshell.util.placement.get_axis2placement's
    in-place ndarray.resize() call on the 2-element DirectionRatios."""
    ifc_file = ifcopenshell.file()
    position = ifc_file.createIfcAxis2Placement2D(
        Location=ifc_file.createIfcCartesianPoint((0.0, 0.0)),
        RefDirection=ifc_file.createIfcDirection((1.0, 0.0)),
    )
    profile = ifc_file.createIfcCircleProfileDef(ProfileType="AREA", ProfileName=None, Position=position, Radius=2.0)
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)  # must not raise

    assert len(loops) == 1
    assert loops[0][0].x == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# _derive_points_from_rectangle -- powers IfcRectangleProfileDef
# ---------------------------------------------------------------------------


def test_derive_points_from_rectangle_returns_centered_closed_loop():
    generator = make_generator()

    points = generator._derive_points_from_rectangle(
        Matrix.Identity(4), elevation=1.0, position=None, x_dim=4.0, y_dim=2.0
    )

    assert len(points) == 5
    assert points[0] == points[-1]
    xs = sorted({round(p.x, 6) for p in points})
    ys = sorted({round(p.y, 6) for p in points})
    assert xs == [-2.0, 2.0]
    assert ys == [-1.0, 1.0]
    assert all(p.z == 1.0 for p in points)


def test_derive_points_from_rectangle_is_wound_counter_clockwise():
    generator = make_generator()

    points = generator._derive_points_from_rectangle(
        Matrix.Identity(4), elevation=0.0, position=None, x_dim=2.0, y_dim=2.0
    )

    assert tool.Cad.is_counter_clockwise_order(points[0], points[1], points[2])


def test_derive_points_from_rectangle_applies_world_matrix_rotation_and_translation():
    """Regression test: a rectangle profile fitted by 'Convert To Rectangle
    Extrusion' bakes its real offset/rotation into IfcExtrudedAreaSolid.Position
    (not profile.Position, which stays None) -- derive_from_slab must fold
    that into world_matrix, or generated walls end up translated/rotated
    away from the actual slab footprint."""
    generator = make_generator()
    # 90-degree rotation about Z plus a translation, standing in for
    # slab_obj.matrix_world combined with a non-identity extrusion Position.
    world_matrix = Matrix.Translation(Vector((10.0, 0.0, 0.0))) @ Matrix.Rotation(math.radians(90), 4, "Z")

    points = generator._derive_points_from_rectangle(world_matrix, elevation=0.0, position=None, x_dim=4.0, y_dim=2.0)

    # Each local corner (+-2, +-1) rotates 90 deg CCW about Z then translates by (10, 0).
    # Note two corners end up sharing a world Y (both local corners with x=2 map to
    # world y=2), so the check must compare the full point set, not a single axis.
    transformed = {(round(p.x, 6), round(p.y, 6)) for p in points[:-1]}
    assert transformed == {(11.0, -2.0), (11.0, 2.0), (9.0, 2.0), (9.0, -2.0)}


# ---------------------------------------------------------------------------
# _get_profile_loops -- the actual bug fix: IfcCircleProfileDef /
# IfcRectangleProfileDef (and hollow variants) no longer crash on the
# missing OuterCurve attribute, and InnerCurves now produce extra loops.
# ---------------------------------------------------------------------------


def test_get_profile_loops_handles_circle_profile_def_without_crashing():
    """Regression test: IfcCircleProfileDef has no OuterCurve attribute, so
    the pre-fix code (`profile.OuterCurve`) raised AttributeError here --
    the same bug class the PR fixed for IfcCompositeProfileDef."""
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcCircleProfileDef(ProfileType="AREA", ProfileName=None, Position=None, Radius=2.0)
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 1
    assert len(loops[0]) > 3


def test_get_profile_loops_handles_rectangle_profile_def_without_crashing():
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcRectangleProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, XDim=4.0, YDim=2.0
    )
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 1
    assert len(loops[0]) == 5


def test_get_profile_loops_circle_hollow_adds_inner_void_loop():
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcCircleHollowProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, Radius=2.0, WallThickness=0.5
    )
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 2
    assert loops[0][0].x == pytest.approx(2.0)
    assert loops[1][0].x == pytest.approx(1.5)


def test_get_profile_loops_rectangle_hollow_adds_inner_void_loop():
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcRectangleHollowProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, XDim=4.0, YDim=2.0, WallThickness=0.5
    )
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 2
    outer_xs = sorted({round(p.x, 6) for p in loops[0]})
    inner_xs = sorted({round(p.x, 6) for p in loops[1]})
    assert outer_xs == [-2.0, 2.0]
    assert inner_xs == [-1.5, 1.5]  # 4.0/2 - 0.5 wall thickness


def test_get_profile_loops_hollow_profile_skips_inner_loop_when_thickness_closes_it():
    """A wall thickness >= half the outer dimension collapses the inner void
    to zero/negative -- must not emit a degenerate/inverted inner loop."""
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcCircleHollowProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, Radius=1.0, WallThickness=1.0
    )
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 1


def test_get_profile_loops_arbitrary_profile_with_voids_adds_inner_loops():
    ifc_file = ifcopenshell.file()

    def polyline(coords):
        return ifc_file.createIfcPolyline(Points=[ifc_file.createIfcCartesianPoint(c) for c in coords])

    outer = polyline([(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0), (-2.0, -2.0)])
    inner = polyline([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)])
    profile = ifc_file.createIfcArbitraryProfileDefWithVoids(
        ProfileType="AREA", ProfileName=None, OuterCurve=outer, InnerCurves=[inner]
    )
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 2
    assert len(loops[0]) == 5
    assert len(loops[1]) == 5


def test_get_profile_loops_arbitrary_closed_profile_has_no_extra_loops():
    ifc_file = ifcopenshell.file()
    outer = ifc_file.createIfcPolyline(
        Points=[
            ifc_file.createIfcCartesianPoint(c)
            for c in [(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0), (-2.0, -2.0)]
        ]
    )
    profile = ifc_file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", ProfileName=None, OuterCurve=outer)
    generator = make_generator()

    loops = generator._get_profile_loops(Matrix.Identity(4), elevation=0.0, profile=profile)

    assert len(loops) == 1


# ---------------------------------------------------------------------------
# derive_from_slab -- end to end: composite profiles, parameterized
# profiles, and inner voids all become their own wall ring, with the
# expected winding (outer CCW, void CW) so wall thickness offsets away
# from the slab's solid area either way.
# ---------------------------------------------------------------------------


def test_derive_from_slab_generates_ring_per_loop_and_winds_voids_opposite_outer():
    ifc_file = ifcopenshell.file()

    def polyline(coords):
        return ifc_file.createIfcPolyline(Points=[ifc_file.createIfcCartesianPoint(c) for c in coords])

    # Outer boundary, authored counter-clockwise.
    outer = polyline([(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0), (-2.0, -2.0)])
    # Inner void, deliberately authored with the *same* winding as the outer
    # loop so the reversal logic in derive_from_slab has to do real work.
    inner = polyline([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)])
    profile = ifc_file.createIfcArbitraryProfileDefWithVoids(
        ProfileType="AREA", ProfileName=None, OuterCurve=outer, InnerCurves=[inner]
    )
    extrusion = Mock(SweptArea=profile, Position=None)

    generator = make_generator()
    generator.container_obj = Mock(location=Vector((0.0, 0.0, 5.0)))
    slab_obj = make_slab_obj()

    recorded_walls = []

    def fake_create_wall_from_2_points(coords, should_round=False):
        wall = {"coords": coords, "obj": Mock()}
        recorded_walls.append(wall)
        return wall

    generator.create_wall_from_2_points = fake_create_wall_from_2_points

    with (
        patch.object(tool.Ifc, "get_entity", return_value=Mock()),
        patch.object(ifcopenshell.util.element, "get_container", return_value=Mock()),
        patch.object(tool.Ifc, "get_object", return_value=generator.container_obj),
        patch.object(ifcopenshell.util.representation, "get_representation", return_value=Mock()),
        patch.object(tool.Model, "get_extrusion", return_value=extrusion),
        patch("bonsai.bim.module.model.wall.bpy") as mock_bpy,
    ):
        mock_bpy.context.active_object = slab_obj
        wall_groups = generator.derive_from_slab()

    assert len(wall_groups) == 2
    outer_loop, inner_loop = wall_groups
    assert len(outer_loop) == 4  # 5-point closed square -> 4 wall segments
    assert len(inner_loop) == 4

    outer_points = polyline_points_from_walls(outer_loop)
    inner_points = polyline_points_from_walls(inner_loop)

    assert tool.Cad.is_counter_clockwise_order(outer_points[0], outer_points[1], outer_points[2])
    # Authored with the same winding as the outer loop, but derive_from_slab
    # must flip void loops so they end up wound the opposite way.
    assert not tool.Cad.is_counter_clockwise_order(inner_points[0], inner_points[1], inner_points[2])


def test_derive_from_slab_handles_composite_of_parameterized_profiles():
    """End-to-end regression: a slab whose SweptArea is an
    IfcCompositeProfileDef made of parameterized (circle/rectangle)
    profiles previously crashed on `profile.OuterCurve` for each member."""
    ifc_file = ifcopenshell.file()
    circle = ifc_file.createIfcCircleProfileDef(ProfileType="AREA", ProfileName=None, Position=None, Radius=1.0)
    rectangle = ifc_file.createIfcRectangleProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, XDim=2.0, YDim=2.0
    )
    composite = ifc_file.createIfcCompositeProfileDef(ProfileType="AREA", Profiles=[circle, rectangle])
    extrusion = Mock(SweptArea=composite, Position=None)

    generator = make_generator()
    generator.container_obj = Mock(location=Vector((0.0, 0.0, 0.0)))
    slab_obj = make_slab_obj()
    generator.create_wall_from_2_points = lambda coords, should_round=False: {"coords": coords, "obj": Mock()}

    with (
        patch.object(tool.Ifc, "get_entity", return_value=Mock()),
        patch.object(ifcopenshell.util.element, "get_container", return_value=Mock()),
        patch.object(tool.Ifc, "get_object", return_value=generator.container_obj),
        patch.object(ifcopenshell.util.representation, "get_representation", return_value=Mock()),
        patch.object(tool.Model, "get_extrusion", return_value=extrusion),
        patch("bonsai.bim.module.model.wall.bpy") as mock_bpy,
    ):
        mock_bpy.context.active_object = slab_obj
        wall_groups = generator.derive_from_slab()  # must not raise AttributeError

    assert len(wall_groups) == 2  # one ring per profile in the composite


def test_derive_from_slab_applies_extrusion_position_for_rectangle_profile():
    """Regression test for a real bug: "Convert To Rectangle Extrusion" (and
    Circle) bakes the profile's real offset/rotation into
    IfcExtrudedAreaSolid.Position, not profile.Position (which stays None).
    Before this fix, derive_from_slab only read profile.Position, so
    generated walls came out with correct dimensions but translated/rotated
    away from the slab's actual footprint."""
    ifc_file = ifcopenshell.file()
    profile = ifc_file.createIfcRectangleProfileDef(
        ProfileType="AREA", ProfileName=None, Position=None, XDim=4.0, YDim=2.0
    )
    # 90-degree rotation about Z (RefDirection (0,1,0) instead of default (1,0,0))
    # plus a translation of (10, 0, 0) -- verified against
    # ifcopenshell.util.placement.get_axis2placement directly.
    extrusion_position = ifc_file.createIfcAxis2Placement3D(
        Location=ifc_file.createIfcCartesianPoint((10.0, 0.0, 0.0)),
        Axis=None,
        RefDirection=ifc_file.createIfcDirection((0.0, 1.0, 0.0)),
    )
    extrusion = Mock(SweptArea=profile, Position=extrusion_position)

    generator = make_generator()
    generator.container_obj = Mock(location=Vector((0.0, 0.0, 0.0)))
    slab_obj = make_slab_obj()  # identity matrix_world -- isolates the extrusion Position effect
    generator.create_wall_from_2_points = lambda coords, should_round=False: {"coords": coords, "obj": Mock()}

    with (
        patch.object(tool.Ifc, "get_entity", return_value=Mock()),
        patch.object(ifcopenshell.util.element, "get_container", return_value=Mock()),
        patch.object(tool.Ifc, "get_object", return_value=generator.container_obj),
        patch.object(ifcopenshell.util.representation, "get_representation", return_value=Mock()),
        patch.object(tool.Model, "get_extrusion", return_value=extrusion),
        patch("bonsai.bim.module.model.wall.bpy") as mock_bpy,
    ):
        mock_bpy.context.active_object = slab_obj
        wall_groups = generator.derive_from_slab()

    assert len(wall_groups) == 1
    points = polyline_points_from_walls(wall_groups[0])
    # Each local rectangle corner (+-2, +-1) rotates 90deg CCW about Z then
    # translates by (10, 0). If extrusion.Position were ignored (the bug),
    # these would instead sit at the untransformed (+-2, +-1).
    transformed = {(round(p.x, 6), round(p.y, 6)) for p in points[:-1]}
    assert transformed == {(11.0, -2.0), (11.0, 2.0), (9.0, 2.0), (9.0, -2.0)}
