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

"""Pure-math tests for the bend tessellation helpers (FIXME #8106).

Pins the geometry contracts the hand-meshed bend body relies on while the
upstream IfcSweptDiskSolid round-trip is broken:

- profile cross-section sampling for circle / rectangle / unsupported
- parallel-transport framing along the centerline (the contract that
  eliminates the twist a fixed world-reference basis produces)
- ``initial_basis`` override that aligns the cross-section with the
  source segment's local +X / +Y axes (the asymmetric-rectangle fix)"""

from math import cos, pi, sin
from unittest.mock import Mock

import bpy
import pytest
from mathutils import Vector

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# _bend_profile_cross_section — IFC profile → 2D sample points
# ---------------------------------------------------------------------------


def test_profile_cross_section_circle_returns_evenly_spaced_ring():
    """Circle profiles sample 16 points by default, equally spaced around
    the radius. First vert sits at ``(radius, 0)`` so the mesh's local
    angular zero aligns with the sweep basis ``right`` axis."""
    from bonsai.bim.module.model.mep import _bend_profile_cross_section

    profile = Mock()
    profile.Radius = 0.1
    profile.is_a = lambda c: c == "IfcCircleProfileDef"

    pts = _bend_profile_cross_section(profile)
    assert pts is not None
    assert len(pts) == 16
    assert pts[0] == pytest.approx((0.1, 0.0))
    # All points lie on the circle.
    for x, y in pts:
        assert (x * x + y * y) == pytest.approx(0.1 * 0.1, abs=1e-9)


def test_profile_cross_section_circle_respects_n_circle_parameter():
    """The sample count is configurable; verify a non-default value
    flows through to the result length."""
    from bonsai.bim.module.model.mep import _bend_profile_cross_section

    profile = Mock()
    profile.Radius = 0.05
    profile.is_a = lambda c: c == "IfcCircleProfileDef"

    pts = _bend_profile_cross_section(profile, n_circle=8)
    assert len(pts) == 8


def test_profile_cross_section_rectangle_returns_four_corners():
    """Rectangle profiles return exactly four corners, in the canonical
    ``[(-X/2,-Y/2), (X/2,-Y/2), (X/2,Y/2), (-X/2,Y/2)]`` winding."""
    from bonsai.bim.module.model.mep import _bend_profile_cross_section

    profile = Mock()
    profile.XDim = 0.4
    profile.YDim = 0.2
    profile.is_a = lambda c: c == "IfcRectangleProfileDef"

    pts = _bend_profile_cross_section(profile)
    assert pts == [(-0.2, -0.1), (0.2, -0.1), (0.2, 0.1), (-0.2, 0.1)]


def test_profile_cross_section_unsupported_returns_none():
    """Profiles other than circle / rectangle (e.g.
    ``IfcArbitraryClosedProfileDef``) return ``None`` so the tessellation
    helper skips the rep swap rather than building geometry against the
    wrong cross-section."""
    from bonsai.bim.module.model.mep import _bend_profile_cross_section

    profile = Mock()
    profile.is_a = lambda c: c == "IfcArbitraryClosedProfileDef"

    assert _bend_profile_cross_section(profile) is None


# ---------------------------------------------------------------------------
# _sweep_profile_along_polyline — vert + face count + parallel transport
# ---------------------------------------------------------------------------


def test_sweep_along_straight_polyline_builds_closed_tube_with_caps():
    """Straight 3-ring centerline + 4-vert profile yields 12 ring verts,
    3 quads × 4 sides = 12 side quads, plus two end-cap triangles per end
    (4-vert profile fans into 2 triangles)."""
    from bonsai.bim.module.model.mep import _sweep_profile_along_polyline

    centerline = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), Vector((0.0, 0.0, 2.0))]
    profile_2d = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]

    verts, faces = _sweep_profile_along_polyline(centerline, profile_2d)

    assert len(verts) == 3 * 4, "3 rings × 4 profile verts"
    # 2 ring gaps × 4 quads each = 8 side faces; 2 caps × 2 triangles = 4 cap faces.
    quad_count = sum(1 for f in faces if len(f) == 4)
    tri_count = sum(1 for f in faces if len(f) == 3)
    assert quad_count == 8, "one quad per profile edge per ring gap"
    assert tri_count == 4, "fan triangulation gives n_profile - 2 = 2 tris per cap"


def test_sweep_parallel_transports_basis_around_right_angle_corner():
    """L-shaped centerline (turn from +Z to +X). After the corner, the
    cross-section's reference direction is rotated 90° from before — the
    parallel-transport invariant. Pin via the first verts of the start
    and end rings: starts perpendicular to +Z (so in XY), ends
    perpendicular to +X (so in YZ)."""
    from bonsai.bim.module.model.mep import _sweep_profile_along_polyline

    centerline = [
        Vector((0.0, 0.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
        Vector((1.0, 0.0, 1.0)),
        Vector((2.0, 0.0, 1.0)),
    ]
    # Single-vert profile would degenerate; use a 4-vert square so we
    # have something to project onto each ring's basis.
    profile_2d = [(0.1, 0.0), (0.0, 0.1), (-0.1, 0.0), (0.0, -0.1)]

    verts, _ = _sweep_profile_along_polyline(centerline, profile_2d)

    # First ring's verts must lie in a plane perpendicular to +Z (the
    # tangent at the first ring). Verify each vert has |z-ring_center.z| ≈ 0.
    first_ring = verts[0:4]
    for v in first_ring:
        assert v.z == pytest.approx(0.0, abs=1e-6), f"first-ring vert off the start plane: {v}"

    # Last ring's tangent is +X (last centerline segment). Verts should
    # lie in a plane perpendicular to +X — i.e. x ≈ 2.0 (the centerline's
    # x at the last ring).
    last_ring = verts[-4:]
    for v in last_ring:
        assert v.x == pytest.approx(2.0, abs=1e-6), f"last-ring vert off the end plane: {v}"


def test_sweep_initial_basis_override_aligns_first_ring_with_segment_axes():
    """The asymmetric-rectangle fix: caller supplies the segment's local
    +X / +Y axes (in world space) as ``initial_basis``; the helper uses
    those as the first ring's basis instead of the world-Z seed. Verify
    by checking that the first profile vert lands at ``ring0 + right *
    sx + up * sy`` for the provided right / up."""
    from bonsai.bim.module.model.mep import _sweep_profile_along_polyline

    centerline = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0))]
    # Profile sample at (0.5, 0) — a single point on the +X profile axis.
    profile_2d = [(0.5, 0.0)]

    # Initial basis where right = +Y world, up = +X world (rotated 90°
    # from the default world-Z seed which would give right ≈ -Y).
    initial_basis = (Vector((0.0, 1.0, 0.0)), Vector((1.0, 0.0, 0.0)))

    verts, _ = _sweep_profile_along_polyline(centerline, profile_2d, initial_basis=initial_basis)

    # First vert = ring0 (0,0,0) + right * 0.5 + up * 0 = (0, 0.5, 0).
    assert tuple(verts[0]) == pytest.approx((0.0, 0.5, 0.0), abs=1e-6)


def test_sweep_default_seed_uses_world_z_reference():
    """Without an ``initial_basis``, the helper falls back to a stable
    world-Z reference for the first ring. Pin so a future refactor of
    the fallback doesn't silently change the orientation for callers
    that rely on the default (the bend preview decorator's debug draw
    path, for instance)."""
    from bonsai.bim.module.model.mep import _sweep_profile_along_polyline

    centerline = [Vector((0.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0))]
    profile_2d = [(1.0, 0.0)]

    verts, _ = _sweep_profile_along_polyline(centerline, profile_2d)

    # First tangent = +X. world-Z up_ref → right = tangent × up_ref =
    # (1,0,0) × (0,0,1) = (0,-1,0). up = right × tangent = (0,0,1).
    # First vert at right * 1.0 = (0, -1, 0).
    assert tuple(verts[0]) == pytest.approx((0.0, -1.0, 0.0), abs=1e-6)
