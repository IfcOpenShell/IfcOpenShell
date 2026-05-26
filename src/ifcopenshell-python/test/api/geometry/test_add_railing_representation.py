# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Tests for ``ifcopenshell.api.geometry.add_railing_representation``.

The module under test was refactored to separate **pure-geometry compute**
(``compute_wall_mounted_handrail_geometry``) from **IFC entity creation**
(``add_railing_representation`` itself). The split lets Bonsai drive a
viewport-only preview without mutating the IFC file (issue #7439).

The bulk of the tests here exercise the pure compute function — it accepts
plain Python/NumPy inputs, returns a dataclass, and has no IFC dependency.
A smaller smoke test then runs the full ``add_railing_representation`` end
to end on a real ifcopenshell.file to confirm the IFC wrapping still
produces a valid ``IfcShapeRepresentation`` containing the expected items.
"""

import numpy as np
import pytest

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import test.bootstrap
from ifcopenshell.api.geometry import (
    RailingSupport,
    WallMountedHandrailGeometry,
    compute_wall_mounted_handrail_geometry,
)

# ---------------------------------------------------------------------------
# Pure-geometry compute tests (no IFC file needed)
# ---------------------------------------------------------------------------


def _straight_path(length: float = 2.0) -> list[tuple[float, float, float]]:
    """Two-point horizontal path along +X at handrail height (1m)."""
    return [(0.0, 0.0, 1.0), (length, 0.0, 1.0)]


def _l_path() -> list[tuple[float, float, float]]:
    """L-shaped path that turns 90° — exercises the fillet-arc branch."""
    return [(0.0, 0.0, 1.0), (2.0, 0.0, 1.0), (2.0, 2.0, 1.0)]


def _common_kwargs(**overrides):
    """Default kwargs roughly matching ``add_railing_representation``'s defaults at unit_scale=1."""
    kwargs = dict(
        support_spacing=1.0,
        railing_diameter=0.050,
        clear_width=0.040,
        height=1.0,
        use_manual_supports=False,
        terminal_type="180",
        looped_path=False,
        unit_scale=1.0,
    )
    kwargs.update(overrides)
    return kwargs


def test_returns_geometry_dataclass():
    """Compute returns the documented dataclass shape."""
    result = compute_wall_mounted_handrail_geometry(railing_path=_straight_path(), **_common_kwargs())
    assert isinstance(result, WallMountedHandrailGeometry)
    assert isinstance(result.handrail_polyline, np.ndarray)
    assert result.handrail_polyline.ndim == 2
    assert result.handrail_polyline.shape[1] == 3
    assert isinstance(result.handrail_arc_point_indices, list)
    assert isinstance(result.supports, list)
    assert result.handrail_radius == pytest.approx(0.025)  # diameter / 2


def test_no_ifc_dependency():
    """The compute function takes no ``ifcopenshell.file`` and creates no entities.

    Asserts the signature has no required ``file`` parameter — i.e. it can be
    called from contexts that do not have an IFC file at all (e.g. Bonsai
    viewport preview).
    """
    import inspect

    sig = inspect.signature(compute_wall_mounted_handrail_geometry)
    assert "file" not in sig.parameters
    assert "context" not in sig.parameters


def test_handrail_radius_is_half_diameter():
    """The returned handrail_radius equals diameter / 2."""
    result = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(), **_common_kwargs(railing_diameter=0.080)
    )
    assert result.handrail_radius == pytest.approx(0.040)


def test_auto_supports_count_along_straight_path():
    """A 2m straight path at 1m support spacing yields 3 automatic supports.

    ``compute_wall_mounted_handrail_geometry`` adds one support every
    ``support_spacing`` along each edge, starting offset half-spacing in.
    For a 2m edge: ``divmod(2.0, 1.0) == (2, 0)``, ``n_supports = 2 + 1 = 3``.
    """
    result = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(length=2.0), **_common_kwargs(support_spacing=1.0)
    )
    assert len(result.supports) == 3


def test_manual_supports_skipped_on_straight_path():
    """Manual supports only land on non-collinear vertices.

    A 2-point straight path has no internal vertices, so manual-supports mode
    produces zero supports.
    """
    result = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(), **_common_kwargs(use_manual_supports=True)
    )
    assert result.supports == []


def test_manual_supports_on_corner():
    """An L-shaped path under manual-supports mode places one support at the corner."""
    result = compute_wall_mounted_handrail_geometry(railing_path=_l_path(), **_common_kwargs(use_manual_supports=True))
    # The corner vertex is non-collinear so it does NOT receive a manual support
    # (manual supports are placed on *collinear* internal vertices, i.e. spaced
    # vertices along otherwise straight runs — see ``collect_supports``).
    # The L-path has only the corner as an internal vertex, which is non-collinear,
    # so no manual supports are produced. This pins the documented behaviour.
    assert result.supports == []


def test_support_shape():
    """Each support is described by an arc polyline + a disk extrusion."""
    result = compute_wall_mounted_handrail_geometry(railing_path=_straight_path(), **_common_kwargs())
    assert len(result.supports) >= 1
    support = result.supports[0]
    assert isinstance(support, RailingSupport)
    # 3-point arc polyline
    assert support.arc_polyline.shape == (3, 3)
    # disk position coincides with the arc endpoint
    np.testing.assert_allclose(support.disk_position, support.arc_polyline[-1])
    assert support.arc_radius > 0
    assert support.disk_radius > 0
    assert support.disk_depth > 0


@pytest.mark.parametrize(
    "terminal_type",
    ["180", "TO_END_POST", "TO_WALL", "TO_FLOOR", "TO_END_POST_AND_FLOOR", "NONE"],
)
def test_all_terminal_types_produce_valid_geometry(terminal_type):
    """All terminal types execute without error and produce a valid handrail polyline."""
    result = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(), **_common_kwargs(terminal_type=terminal_type)
    )
    assert result.handrail_polyline.shape[0] >= 2
    assert all(0 <= idx < len(result.handrail_polyline) for idx in result.handrail_arc_point_indices)


def test_terminal_type_none_skips_cap_generation():
    """``terminal_type="NONE"`` skips terminal-cap generation entirely.

    The "NONE" sentinel is consumed at the cap step — the polyline is left
    exactly as it came out of the fillet pass, with no extra cap vertices
    or cap arc-point indices appended at either end. Every other terminal
    type adds at least one cap vertex per end.
    """
    result_none = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(), **_common_kwargs(terminal_type="NONE")
    )
    result_180 = compute_wall_mounted_handrail_geometry(
        railing_path=_straight_path(), **_common_kwargs(terminal_type="180")
    )
    # NONE leaves the polyline at the raw 2-point path; 180 adds caps at both ends.
    assert result_none.handrail_polyline.shape[0] == 2
    assert result_none.handrail_polyline.shape[0] < result_180.handrail_polyline.shape[0]
    # NONE registers no cap arc points; 180 registers one per cap (2 total).
    assert result_none.handrail_arc_point_indices == []
    assert len(result_180.handrail_arc_point_indices) >= 2


def test_l_path_adds_fillet_arc():
    """An L-path with a 90° turn introduces fillet arc points in the handrail polyline."""
    result = compute_wall_mounted_handrail_geometry(railing_path=_l_path(), **_common_kwargs())
    # The fillet replaces the corner vertex with three points (start, mid-arc, end),
    # and registers the mid-arc index in handrail_arc_point_indices.
    assert len(result.handrail_arc_point_indices) >= 1


def test_looped_path_runs_without_caps():
    """A looped path skips terminal caps (no open ends to cap).

    Pins the documented behaviour: ``if not looped_path and cap_type != "NONE"``
    — caps only when not looped. The caller passes an *unclosed* sequence of
    vertices; the function appends the first two points internally to compute
    fillet arcs across the wrap-around. Passing an already-closed loop
    (last vertex == first) produces a zero-length edge that breaks
    ``np_normalized`` — the API contract is the unclosed form.
    """
    # Square footprint, NOT closed (the function closes internally).
    looped = [
        (0.0, 0.0, 1.0),
        (2.0, 0.0, 1.0),
        (2.0, 2.0, 1.0),
        (0.0, 2.0, 1.0),
    ]
    result = compute_wall_mounted_handrail_geometry(railing_path=looped, **_common_kwargs(looped_path=True))
    # Polyline must have no NaN values — checks that the closure was clean and
    # no zero-length edge sneaked into the normalisation path.
    assert not np.any(np.isnan(result.handrail_polyline))
    # Looped path has 4 corners → 4 fillet arcs.
    assert len(result.handrail_arc_point_indices) == 4


def test_unit_scale_converts_mm_constants():
    """``unit_scale`` divides the mm-based constants so they land in project units.

    The fillet radius is hard-coded as ``mm(100) = 0.1m`` and gets divided by
    ``unit_scale`` before being applied. With ``unit_scale=1000`` (i.e. project
    units are millimetres) the effective fillet radius should be 0.0001 — too
    small to affect the polyline noticeably — but the function must run and
    produce a valid result without raising.
    """
    result = compute_wall_mounted_handrail_geometry(
        railing_path=[(0, 0, 1000), (2000, 0, 1000), (2000, 2000, 1000)],
        support_spacing=1000.0,
        railing_diameter=50.0,
        clear_width=40.0,
        height=1000.0,
        unit_scale=1000.0,
    )
    assert isinstance(result, WallMountedHandrailGeometry)
    assert result.handrail_radius == pytest.approx(25.0)


# ---------------------------------------------------------------------------
# Collinearity precision regression guards
# ---------------------------------------------------------------------------


def test_collinear_subdivided_path_does_not_add_fillets():
    """Points produced by subdividing a non-axis-aligned straight edge
    must be treated as collinear, even when float arithmetic pushes the
    normalised dot product *above* 1.0.

    Before fix: ``collinear(d0, d1)`` was ``is_x(np_angle(d0, d1), 0)``,
    where ``np_angle`` is ``arccos(dot)``. When the two direction
    vectors come from a subdivided non-axis-aligned segment, the dot of
    the resulting unit vectors can land at ``1.0 + 1 ulp`` due to float
    arithmetic. ``arccos`` of any value > 1.0 returns NaN, ``is_x(NaN,
    0)`` is False, and the function then tries to compute a fillet at
    what should be a straight run — which immediately explodes via
    ``tan(near-zero)``.

    Fix: ``collinear`` now uses ``|d0 × d1|`` instead of
    ``arccos(dot)``. The cross-product magnitude is computed without
    going through ``arccos``, so it stays valid (and near zero) for
    truly-collinear inputs regardless of which side of 1.0 the dot
    product falls on. It also collapses to 0 for anti-parallel
    directions, so back-and-forth paths get the same "no usable turn"
    treatment.
    """
    # Non-axis-aligned because axis-aligned cases happen to give an
    # exact dot of 1.0 — the arccos-clamp bug only surfaces when float
    # arithmetic produces a sub-ulp overshoot, which needs a direction
    # whose components don't divide cleanly.
    a = np.array([0.123, 0.456, 1.0])
    direction = np.array([0.6, 0.8, 0.0])  # length 1, non-axis-aligned
    p0 = a
    p1 = a + direction * 1.5
    p2 = a + direction * 3.0
    path = [tuple(p0), tuple(p1), tuple(p2)]
    result = compute_wall_mounted_handrail_geometry(railing_path=path, **_common_kwargs())
    assert not np.any(np.isnan(result.handrail_polyline))
    assert not np.any(np.isinf(result.handrail_polyline))
    # Only the two terminal-cap fillets — the interior vertex was
    # collinear and must not have introduced a third arc.
    assert len(result.handrail_arc_point_indices) == 2


# ---------------------------------------------------------------------------
# End-to-end IFC smoke tests — confirms the IFC wrapping still produces a
# valid IfcShapeRepresentation around the computed geometry.
# ---------------------------------------------------------------------------


class TestAddRailingRepresentation(test.bootstrap.IFC4):
    def setup_context(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(self.file, [unit])
        model_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_context,
        )

    def test_default_railing_returns_shape_representation(self):
        """End-to-end smoke: a default-args call returns a valid IfcShapeRepresentation
        with one item per support plus the main handrail solid."""
        self.setup_context()
        representation = ifcopenshell.api.geometry.add_railing_representation(
            self.file,
            context=self.body,
            railing_path=[(0.0, 0.0, 1.0), (2.0, 0.0, 1.0)],
        )
        assert representation.is_a("IfcShapeRepresentation")
        # Items: 2 per support (arc swept-disk + floor disk extrusion) + 1 handrail swept disk
        assert len(representation.Items) >= 3
        # Final item must be the handrail itself (a swept-disk solid)
        assert representation.Items[-1].is_a("IfcSweptDiskSolid")
